program main
   use variable
   use dictionary
   implicit none
   type(dictionary_t) :: data
   integer :: n
   real :: dt
   character(20) :: title
   data = ('steps'.kv.25)//('dt'.kv.0.125)//('title'.kv.'playground')
   if (len(data) /= 3) error stop 'dictionary size'
   call assign(n,data,'steps')
   call assign(dt,data,'dt')
   call assign(title,data,'title')
   if (n /= 25 .or. dt /= 0.125 .or. trim(title) /= 'playground') error stop 'lookup'
   print '(a,i0)', 'Steps: ', n
   print '(a,f7.3)', 'Time step: ', dt
   print '(a)', 'Title: '//trim(title)
   data = data//('steps'.kv.50)
   call assign(n,data,'steps')
   if (n /= 50 .or. len(data) /= 3) error stop 'replacement'
   call delete(data,'dt')
   if (len(data) /= 2) error stop 'deletion'
   call delete(data)
   print '(a)', 'PASS fdict'
end program main
