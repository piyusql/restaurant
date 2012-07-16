from booking.models import Table, TableAllocation, DEFAULT_BOOKING_SLOT
from datetime import datetime, timedelta
from django.db.models import Q
from django.db import transaction, IntegrityError
from django.shortcuts import render_to_response
from django.template import RequestContext
# Create your views here.

def index(request):
    message = "see the status of reataurant bookings."
    tables = Table.objects.all()
    if tables.count() == 0:
        create_factory_settings()
    tables = Table.objects.filter(is_active = True)
    bookings = TableAllocation.objects.filter(end_time__gt = datetime.now()).order_by('-start_time')
    return render_to_response('bookings.html', {'tables' : tables, 'bookings':bookings, 'message' : message}, context_instance=RequestContext(request))

def make_booking(request):
    message = "please fill the info to make booking"
    guest_count = guest_name = contact_no = ''
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    end_time = (datetime.now() + timedelta(hours = DEFAULT_BOOKING_SLOT)).strftime("%Y-%m-%d %H:%M")
    if request.method == "POST":
        guest_name = request.REQUEST.get('guest_name')
        contact_no = request.REQUEST.get('contact_no')
        guest_count = int(request.REQUEST.get('guest_count'))
        start_time = datetime.strptime(str(request.REQUEST.get('start_time')),"%Y-%m-%d %H:%M")
        end_time = datetime.strptime(str(request.REQUEST.get('end_time')), "%Y-%m-%d %H:%M")
        message = book_table(guest_count, guest_name, contact_no, start_time, end_time)
    return render_to_response('make_booking.html', {'guest_count' : guest_count, 'start_time': start_time, 'end_time' : end_time,\
            'guest_name' : guest_name, 'contact_no' : contact_no, 'message' : message}, context_instance=RequestContext(request))

def release_booking(request, _id):
    _tableAllocation = TableAllocation.objects.get(id = _id)
    _tableAllocation.release()
    message = "table - %d  released successfully" %(_tableAllocation.table.id)
    tables = Table.objects.filter(is_active = True)
    bookings = TableAllocation.objects.filter(end_time__gt = datetime.now()).order_by('-start_time')
    return render_to_response('bookings.html', {'tables' : tables, 'bookings':bookings, 'message':message}, context_instance=RequestContext(request))


def create_factory_settings():
    #create tables with the following capacity
    for x in [4,4,4,4,2,2,2,6,6]:
        Table.objects.create(capacity = x)

def get_free_tables(start_time, end_time):
    """
        return list of tables which is free for the given timeslot
    """
    _start_time = datetime.now() if not start_time else start_time
    _end_time = _start_time + timedelta(hours = DEFAULT_BOOKING_SLOT) if not end_time else end_time
    tables = filter(
                    lambda _tb : (_tb.allocations.filter(Q(start_time__lt = _start_time, end_time__gt = _start_time)|
                            Q(start_time__lt = _end_time, end_time__gt = _end_time)).count() == 0),
                    Table.objects.filter(is_active = True))
    return [(_tb.id, _tb.capacity) for _tb in tables]

#@transaction.commit_manually
def book_table(guest_count, guest_name, contact_no, start_time, end_time):
    _selected_tables = get_selected_tables(guest_count, start_time, end_time)
    print _selected_tables
    if not _selected_tables:
        return "No table is free for the given time slot and guest list"
    #sid = transaction.savepoint()
    try:
        #TO DO : Add all the following Allocation to a single booking ID
        for _tid in _selected_tables:
            TableAllocation.objects.create(table = Table.objects.get(id = _tid), guest_name = guest_name, contact_no = contact_no, 
                    start_time = start_time, end_time = end_time)
    except IntegrityError as e:
        #transaction.savepoint_rollback(sid)
        #return e.message
        raise
    else:
        pass
        #transaction.commit()
    return "Booking has been successfuly done."

def get_selected_tables(guest_count, start_time, end_time):
    _li = []
    free_tables = get_free_tables(start_time, end_time)
    #simply allot the table as per guest count
    #TO DO : we can choose minimum capacity as per guest count
    for id,cap in free_tables:
        if guest_count > 0:
            guest_count = guest_count - cap
            _li.append(id)
        else:
            break
    if sum(_li) >= guest_count:
        return _li
    return None
