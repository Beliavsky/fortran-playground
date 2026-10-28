! Exact simplex integrals: integral x^a y^b = a! b!/(a+b+2)!,
! and integral x^a y^b z^c = a! b! c!/(a+b+c+3)!.
program demo_cubatures
   use iso_fortran_env, only: dp => real64
   use cubatures, only: cubature, CUB_TRI, CUB_TET
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(cubature) :: q
   real(dp) :: total, exact

   q = cubature(CUB_TRI,4)
   if (.not. q%is_valid()) error stop 'Invalid triangle rule'
   total = sum(q%weights*q%abscissae(1,:)**2*q%abscissae(2,:))
   exact = 1.0_dp/60
   if (.not. ieee_is_finite(total)) error stop 'Nonfinite triangle integral'
   if (abs(total-exact)>1e-13_dp) error stop 'Triangle integral differs'
   print '(a,i0,a,2f18.12)', 'Triangle (',q%npoints,' points), integral and exact:',total,exact
   q = cubature(CUB_TET,4)
   if (.not. q%is_valid()) error stop 'Invalid tetrahedron rule'
   total = sum(q%weights*product(q%abscissae,dim=1))
   exact = 1.0_dp/720
   if (.not. ieee_is_finite(total)) error stop 'Nonfinite tetrahedron integral'
   if (abs(total-exact)>1e-13_dp) error stop 'Tetrahedron integral differs'
   print '(a,i0,a,2f18.12)', 'Tetrahedron (',q%npoints,' points), integral and exact:',total,exact
   print '(a)', 'PASS fortran_cubatures'
end program
