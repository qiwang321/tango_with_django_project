from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category
from rango.models import Page
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rango.forms import CategoryForm, PageForm
from datetime import datetime
from rango.bing_search import run_query
from django.shortcuts import redirect

# Create your views here.

def url_encode(name):
    return name.replace(' ', '_')
def url_decode(name):
    return name.replace('_', ' ')
def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__startswith=starts_with)
    else:
        cat_list = Category.objects.all()
    
    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]
    
    """
    for cat in cat_list:
        cat.url = encode_url(cat.name)
    """
        
    return cat_list



def index(request):
 
    context = RequestContext(request)
    cat_list = get_category_list()
    pages_view = Page.objects.order_by('-views')[:5]
    
    context_dict = {'cat_list': cat_list, 'page_list': pages_view}
    

    category_list = Category.objects.all()
    for category in category_list:
        if len(category.url) == 0:
            category.url = url_encode(category.name)
            category.save()
    """
    response = render_to_response('rango/index.html', context_dict, context)

    # client side cookies
    # get the number of visits to the site.
    visits = int(request.COOKIES.get('visits', '0'))
    
    # Does the cookie last_visit exist?
    if request.COOKIES.has_key('last_visit'):
        last_visit = request.COOKIES['last_visit']
        last_visit_time = datetime.strptime(last_visit, "%Y-%m-%d %H:%M:%S")

        # If it's been more than a day since the last visit...
        if (datetime.now() - last_visit_time).seconds > 5:
            response.set_cookie('visits', visits+1)
            response.set_cookie('last_visit', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    else:
        response.set_cookie('last_visit', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        redponse.set_cookie('visits', 1)

    return response
    """
    
    # server side cookies
    if request.session.get('last_visit'):
        last_visit_time = request.session.get('last_visit')
        visits = request.session.get('visits', 0)
        
        if (datetime.now() - datetime.strptime(last_visit_time, "%Y-%m-%d %H:%M:%S")).seconds > 5:
            request.session['visits'] = visits+1
            request.session['last_visit'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        request.session['last_visit'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        request.session['visits'] = 1
    #print 'visits = ' + str(request.session['visits'])
    #print 'last visit = ' + request.session['last_visit']
    return render_to_response('rango/index.html', context_dict, context)
                



def about(request):
    context = RequestContext(request)
    visits = request.session.get('visits', 0)
    context_dict = {'itmessage': "I am italian font from the context", 'visits': visits, 'cat_list': get_category_list()}
    return render_to_response('rango/about.html', context_dict, context)



def category(request, category_name_url):
    context = RequestContext(request)
    cat_list = Category.objects.order_by('-views')[:5]
    category_name = category_name_url.replace('_', ' ')
    context_dict = {'cat_list': cat_list, 'category_name': category_name}
    try:
        category = Category.objects.get(url=category_name_url)
        page_list = Page.objects.filter(category=category)
        context_dict['page_list'] = page_list
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass

    # the search functionality
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)
            context_dict['result_list'] =  result_list
        
    return render_to_response('rango/category.html', context_dict, context)



# form handling
@login_required
def add_category(request):
    context = RequestContext(request)
    if request.method =='POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()
    context_dict = {'cat_list': get_category_list(), 'form': form}
    return render_to_response('rango/add_category.html', context_dict, context) 

@login_required
def add_page(request, category_name_url):
    context = RequestContext(request)

    category_name = url_decode(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)
        
        if form.is_valid():
            # Not all fields are automatically populated!
            page = form.save(commit=False)

            # Retrieve the associated Category object so we can add it.
            # Wrap the code in a try block - check if the category actually exists
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                return render_to_response('rango/add_category.html', {}, context)
            
            page.views = 0
            page.save()

            return category(request, category_name_url)
        else:
            print form.errors
            
    else:
        form = PageForm()
    context_dict = {'cat_list': get_category_list(),
                    'category_name_url': category_name_url,
                    'category_name': category_name,
                    'form': form}
    
    return render_to_response('rango/add_page.html', context_dict, context)

        


# User views
def register(request):

    context = RequestContext(request)

    registered = False
    
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            
            user.set_password(user.password)
            user.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user
            
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()

            registered = True
        
        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    context_dict = {'user_form': user_form,
                    'profile_form': profile_form,
                    'registered': registered,
                    'cat_list': get_category_list()}

    # Render the template depending on the context
    return render_to_response('rango/register.html', context_dict, context)



def user_login(request):
    context = RequestContext(request)
    context_dict = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/rango/')
            else:
                context_dict['disabled_account'] = True
        else:
            # Bad login details were provided
            print "Invalid login details: {0}, {1}".format(username, password)
            context_dict['bad_details'] = True
        
    context_dict['cat_list'] = get_category_list()

# The request is not a HTTP POST, so display the login form.
    return render_to_response('rango/login.html', context_dict, context)




@login_required
def restricted(request):
    context = RequestContext(request)
    context_dict = {'cat_list': get_category_list()}
    return render_to_response('rango/restricted.html', context_dict, context)

@login_required
def user_logout(request):
    logout(request)
    return redirect('/rango/')



# Search functionality
def search(request):
    context = RequestContext(request)
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)

    context_dict = {'cat_list': get_category_list(), 'result_list': result_list}

    return render_to_response('rango/search.html', context_dict, context)

# View user profile
def profile(request):
    context = RequestContext(request)
    context_dict = {'cat_list': get_category_list()}
    return render_to_response('rango/profile.html', context_dict, context)

# Track page visits
def track_url(request):
    context = RequestContext(request);
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']

    page = Page.objects.filter(id=page_id)[0]
    if page:
        page.views += 1
        page.save()
        return redirect(page.url)
    else:
        return redirect('/rango/')
    

# increment the number of likes
@login_required
def like_category(request):
    context = RequestContext(request)
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        category = Category.objects.get(id=int(cat_id))
        if category:
            likes = category.likes + 1
            category.likes = likes
            category.save()

    return HttpResponse(likes)

# suggest category list
def suggest_category(request):
    context = RequestContext(request)
    cat_list = []
    starts_with = ''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']
        
    cat_list = get_category_list(8, starts_with)
    
    return render_to_response('rango/category_list.html', {'cat_list': cat_list}, context)


# quick add pages
def auto_add_page(request):
    context = RequestContext(request)
    cat_id = None
    url = None
    title = None
    context_dict = {}
    if request.method == 'GET':
        title = request.GET['title']
        url = request.GET['url']
        cat_id = request.GET['category_id']
        
        if cat_id:
            cat = Category.objects.get(id=cat_id)
            Page.objects.get_or_create(category=cat, title=title, url=url)
            page_list = Page.objects.filter(category=cat).order_by('-views')
            
            context_dict['page_list'] = page_list

    return render_to_response('rango/page_list.html', context_dict, context)

