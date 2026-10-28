program main
   use ADdnSVM_m
   use QDUtil_m, only: Rkind
   implicit none
   type(dnS_t) :: x,f
   real(Rkind), allocatable :: d1(:),d2(:,:),d3(:,:,:)
   x=Variable(Val=2._Rkind,nderiv=3)
   f=x**4
   d1=get_d1(f); d2=get_d2(f); d3=get_d3(f)
   if (abs(get_d0(f)-16._Rkind)>1e-10_Rkind) error stop
   if (maxval(abs([d1(1),d2(1,1),d3(1,1,1)]-[32._Rkind,48._Rkind,48._Rkind]))>1e-10_Rkind) error stop
   print '(a,f10.3)', 'f(x)=x**4 at x=2:',get_d0(f)
   print '(a,3f10.3)', 'First, second, third derivatives:',d1(1),d2(1,1),d3(1,1,1)
   print *, 'PASS ad_dnsvm'
end program main
