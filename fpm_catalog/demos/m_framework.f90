program main
   use M_framework__approx, only: in_margin
   implicit none
   real :: computed(3), expected(3)
   computed = [1.0,2.0,3.000001]
   expected = [1.0,2.0,3.0]
   if (.not. all(in_margin(computed,expected,1.e-5))) error stop 'close values rejected'
   if (in_margin(1.0,2.0,1.e-5)) error stop 'different values accepted'
   print *, 'Compared arrays with a relative margin.'
   print *, 'PASS m_framework'
end program
