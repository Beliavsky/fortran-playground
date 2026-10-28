! Gauss-Legendre and Gauss-Hermite rules with independently known integrals.
program demo_qdutillib
   use QDUtil_NumParameters_m, only: Rkind
   use QDUtil_Quadrature_m, only: Quadrature_t, Init_Quadrature, dealloc_Quadrature
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(Quadrature_t) :: q
   real(Rkind) :: value, exact
   integer :: status
   call Init_Quadrature(q,nq=6,name='LegendreP',err=status)
   if (status/=0) error stop 'Legendre initialization failed'
   value = sum(q%w*q%x(1,:)**8)
   exact = 2._Rkind/9._Rkind
   print '(a,f20.14,a,es12.3)', 'Integral of x**8 on [-1,1]: ',value,'  error: ',abs(value-exact)
   if (.not. ieee_is_finite(value)) error stop 'Nonfinite integral'
   if (abs(value-exact)>1e-12_Rkind) error stop 'Legendre quadrature failed'
   call dealloc_Quadrature(q)
   call Init_Quadrature(q,nq=8,name='HO',err=status)
   if (status/=0) error stop 'Hermite initialization failed'
   ! HO weights integrate the full function: include the Gaussian explicitly.
   value = sum(q%w*q%x(1,:)**2*exp(-q%x(1,:)**2))
   exact = sqrt(acos(-1._Rkind))/2._Rkind
   print '(a,f20.14,a,es12.3)', 'Integral of x**2*exp(-x**2): ',value,'  error: ',abs(value-exact)
   if (.not. ieee_is_finite(value)) error stop 'Nonfinite integral'
   if (abs(value-exact)>1e-12_Rkind) error stop 'Hermite quadrature failed'
   call dealloc_Quadrature(q)
   print '(a)', 'PASS qdutillib'
end program
