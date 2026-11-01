! Independent MIT consumer; see licenses/factorization-rules-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: expm
   implicit none
   real(real64) :: a(3,3),original(3,3),expected(3,3),eye(3,3),nilpotent(3,3),rotation(2,2),angle,shift
   real(real64),allocatable :: actual(:,:)
   integer :: t,i,mode,checks
   eye=0
   do i=1,3
      eye(i,i)=1
   end do
   checks=0
   do t=-16,16
      shift=real(t,real64)/16
      nilpotent=0
      nilpotent(1,2)=real(t,real64)/8
      nilpotent(2,3)=real(modulo(t,7)-3,real64)/4
      nilpotent(1,3)=real(modulo(t,5)-2,real64)/8
      a=shift*eye+nilpotent
      original=a
      expected=exp(shift)*(eye+nilpotent+matmul(nilpotent,nilpotent)/2)
      do mode=1,2
         if(mode==1) then
            actual=expm(a)
         else
            actual=expm(a,order=12)
         end if
         if(.not.all(ieee_is_finite(actual))) error stop 'Nonfinite matrix exponential'
         if(maxval(abs(actual-expected))>2.e-11_real64*max(1._real64,maxval(abs(expected)))) &
            error stop 'Shifted nilpotent exponential oracle'
         if(any(a/=original)) error stop 'Exponential input changed'
         checks=checks+9
      end do
      angle=real(t,real64)*acos(-1._real64)/32
      rotation=reshape([0._real64,angle,-angle,0._real64],[2,2])
      expected=0
      expected(1,1)=cos(angle)
      expected(2,2)=cos(angle)
      expected(1,2)=-sin(angle)
      expected(2,1)=sin(angle)
      do mode=1,2
         if(mode==1) then
            actual=expm(rotation)
         else
            actual=expm(rotation,order=12)
         end if
         if(.not.all(ieee_is_finite(actual))) error stop 'Nonfinite rotation exponential'
         if(maxval(abs(actual-expected(:2,:2)))>2.e-11_real64) error stop 'Rotation exponential oracle'
         checks=checks+4
      end do
   end do
   print '(a,i0)', '132 exponential calls; shifted nilpotent and plane-rotation closed-form entries: ',checks
   print '(a)', 'PASS stdlib-expm-reference'
end program
