program main
   use wavepack, only: rk,wavelet
   implicit none
   integer, parameter :: n=256,jtot=49
   real(rk), parameter :: dt=.25_rk,dj=.125_rk,s0=.5_rk,target_period=8._rk
   real(rk) :: signal(n),scale(jtot),period(jtot),coi(n),power(jtot),param
   complex(rk) :: wave(n,jtot)
   integer :: i,j,mother,peak
   do i=1,n
      signal(i)=sin(2._rk*acos(-1._rk)*real(i-1,rk)*dt/target_period)
   end do
   mother=0; param=6._rk ! Morlet wavelet.
   call wavelet(n,signal,dt,mother,param,s0,dj,jtot,n,wave,scale,period,coi)
   do j=1,jtot
      power(j)=sum(abs(wave(n/4:3*n/4,j))**2)/real(n/2+1,rk)
   end do
   peak=maxloc(power,dim=1)
   if (abs(period(peak)-target_period)>.8_rk.or.power(peak)<=0._rk) error stop
   print '(a,f9.4)', 'Generated signal period:',target_period
   print '(a,f9.4)', 'Peak wavelet period:    ',period(peak)
   print *, 'PASS wavepack'
end program main
