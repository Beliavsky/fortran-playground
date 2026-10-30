! Headless PLplot example: no display server or Python plotting process is used.
program main
   use plplot, only: plflt, plsdev, plsfnam, plspage, plinit, plenv, pllab, plline, plend, plgver
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n=201
   real(plflt) :: x(n), y(n), pi
   integer :: i, unit, bytes, ios
   character(len=80) :: version
   character(len=8) :: signature
   logical :: exists
   pi=acos(-1.0_plflt)
   do i=1,n
      x(i)=-pi+2*pi*real(i-1,plflt)/real(n-1,plflt)
   end do
   y=sin(x)
   if (.not.all(ieee_is_finite(y))) error stop 'Nonfinite plot data'
   if (abs(y(51)+1.0_plflt)>1.0e-12_plflt .or. abs(y(151)-1.0_plflt)>1.0e-12_plflt) error stop 'Sine sample check'
   call plgver(version)
   print '(a)', 'PLplot version: '//trim(version)
   call plsdev('pngcairo')
   call plsfnam('plplot-sine.png')
   call plspage(0.0_plflt,0.0_plflt,800,500,0,0)
   call plinit()
   call plenv(-pi,pi,-1.2_plflt,1.2_plflt,0,0)
   call pllab('x (radians)','sin(x)','Sine curve from Fortran with PLplot')
   call plline(x,y)
   call plend()
   inquire(file='plplot-sine.png',exist=exists,size=bytes)
   if (.not.exists .or. bytes<1000) error stop 'PNG not written'
   open(newunit=unit,file='plplot-sine.png',access='stream',form='unformatted',status='old',action='read')
   read(unit,iostat=ios) signature
   close(unit)
   if (ios/=0) error stop 'PNG signature read failed'
   if (signature/=achar(137)//'PNG'//achar(13)//achar(10)//achar(26)//achar(10)) error stop 'Invalid PNG signature'
   print '(a,i0)', 'PNG bytes: ',bytes
   print '(a)', 'PASS plplot'
end program main
