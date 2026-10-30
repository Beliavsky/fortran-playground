module callbacks
contains
 real function one(x)
 real,intent(in)::x
 one=1.0
 end function
end module
program main
 use callbacks
 use module_integrate
 implicit none
 real::values(3)
 values=[rectangle(one,0.0,1.0,10),trapezoidal(one,0.0,1.0,10),simpson(one,0.0,1.0,10)]
 print '(a,3f14.9)', 'Integral of 1 on [0,1], n=10: ',values
 if(any(abs(values-1.0)>1.0e-6)) error stop 'Constant-integrand check failed'
end program
