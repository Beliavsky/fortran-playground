program main
   use splpak_module, only: splpak_type, wp => splpak_wp
   implicit none
   integer, parameter :: n=20, nodes(1)=[10], ncf=10, nwrk=ncf*(ncf+1)+1
   type(splpak_type) :: spline
   real(wp) :: x(1,n), y(n), weights(n), coef(ncf), work(nwrk), value
   integer :: i, status
   do i=1,n
      x(1,i) = real(i-1,wp)/(n-1)
   end do
   y = 2*x(1,:)
   weights = 1.0_wp
   call spline%initialize(1,x,1,y,weights,n,[0.0_wp],[1.0_wp], &
      nodes,1.0_wp,coef,ncf,work,nwrk,status)
   if (status /= 0) error stop 'spline fit failed'
   value = spline%evaluate(1,[0.5_wp],coef,[0.0_wp],[1.0_wp],nodes,status)
   if (status /= 0 .or. abs(value-1.0_wp) > 1.e-8_wp) error stop 'incorrect spline value'
   print *, 'Fitted value of 2*x at x=0.5:', value
   print *, 'PASS splpak'
end program
