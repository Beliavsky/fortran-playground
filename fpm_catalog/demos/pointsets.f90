program main
   use pointsets, only: arithmetic_spacing,geometric_spacing
   use select_precision, only: wp
   implicit none
   real(wp) :: uniform(5),geometric(5)
   call arithmetic_spacing(uniform,0._wp,1._wp)
   call geometric_spacing(geometric,0._wp,1._wp,2._wp)
   if (maxval(abs(uniform-[0._wp,.25_wp,.5_wp,.75_wp,1._wp]))>1e-6_wp) error stop
   if (maxval(abs(geometric-[0._wp,1._wp,3._wp,7._wp,15._wp]/15))>1e-6_wp) error stop
   print '(a,5f9.5)', 'Uniform grid:  ',uniform
   print '(a,5f9.5)', 'Geometric grid:',geometric
   print *, 'PASS pointsets'
end program main
