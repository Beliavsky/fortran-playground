! Modified Bessel functions of fixed orders zero and one.
program demo_bessels
   use bessels, only: BK,besseli0,besseli1,besselk0,besselk1
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(BK),parameter :: x(*)=[0.25_BK,0.5_BK,1._BK,2._BK,8._BK]
   ! Independent reference values at x=1, not computed using this library.
   real(BK),parameter :: reference(*)=[1.2660658777520083356_BK,0.5651591039924850272_BK, &
      0.4210244382407083333_BK,0.6019072301972345747_BK]
   real(BK) :: values(4),identity_error
   integer :: i
   values=[besseli0(1._BK),besseli1(1._BK),besselk0(1._BK),besselk1(1._BK)]
   if (.not.all(ieee_is_finite(values))) error stop 'Nonfinite reference values'
   if (maxval(abs(values-reference))>1e-12_BK) error stop 'Bessel reference check failed'
   print '(a)', 'x            I0(x)            I1(x)            K0(x)            K1(x)     Wronskian error'
   do i=1,size(x)
      values=[besseli0(x(i)),besseli1(x(i)),besselk0(x(i)),besselk1(x(i))]
      if (.not.all(ieee_is_finite(values))) error stop 'Nonfinite Bessel values'
      identity_error=abs(x(i)*(values(1)*values(4)+values(2)*values(3))-1)
      print '(f6.2,4es17.8,es16.3)',x(i),values,identity_error
      if (identity_error>1e-11_BK) error stop 'Bessel Wronskian identity failed'
   end do
   print '(a)', 'PASS fortran-bessels'
end program
