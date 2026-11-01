! Independent MIT consumer; see licenses/activations-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_specialfunctions, only: softmax, logsoftmax, softmax_grad
   implicit none
   real(real64),parameter :: shifts(3)=[-1000._real64,0._real64,1000._real64]
   real(real64),allocatable :: w(:),x(:),saved(:),p(:),logs(:),gradient(:),reference(:)
   real(real64) :: wm(3,4),xm(3,4),savedm(3,4),pm(3,4),lm(3,4),gm(3,4),rm(3,4),denominator
   integer :: n,t,k,i,j,direction,vectors,matrices,entries
   vectors=0; matrices=0; entries=0
   do n=1,12
      allocate(w(n),x(n),saved(n))
      do t=1,4
         do i=1,n
            w(i)=2._real64**(mod(i*t,7)-3)
         end do
         denominator=0
         do i=1,n
            denominator=denominator+w(i)
         end do
         reference=w/denominator
         do k=1,3
            x=log(w)+shifts(k); saved=x
            p=softmax(x); logs=logsoftmax(x); gradient=softmax_grad(x)
            do i=1,n
               call check(p(i),reference(i))
               call check(logs(i),log(reference(i)))
               call check(gradient(i),reference(i)*(1-reference(i)))
            end do
            call check(sum(p),1._real64)
            if(any(x/=saved)) error stop 'Softmax vector input preservation'
            vectors=vectors+1; entries=entries+n
         end do
      end do
      deallocate(w,x,saved)
   end do
   do t=1,4
      do j=1,4
         do i=1,3
            wm(i,j)=2._real64**(mod(i+3*j+t,7)-3)
         end do
      end do
      do direction=1,2
         if(direction==1) then
            do j=1,4
               denominator=0
               do i=1,3
                  denominator=denominator+wm(i,j)
               end do
               rm(:,j)=wm(:,j)/denominator
            end do
         else
            do i=1,3
               denominator=0
               do j=1,4
                  denominator=denominator+wm(i,j)
               end do
               rm(i,:)=wm(i,:)/denominator
            end do
         end if
         do k=1,3
            xm=log(wm)+shifts(k); savedm=xm
            pm=softmax(xm,dim=direction); lm=logsoftmax(xm,dim=direction); gm=softmax_grad(xm,dim=direction)
            do j=1,4
               do i=1,3
                  call check(pm(i,j),rm(i,j))
                  call check(lm(i,j),log(rm(i,j)))
                  call check(gm(i,j),rm(i,j)*(1-rm(i,j)))
               end do
            end do
            if(direction==1) then
               do j=1,4
                  call check(sum(pm(:,j)),1._real64)
               end do
            else
               do i=1,3
                  call check(sum(pm(i,:)),1._real64)
               end do
            end if
            if(any(xm/=savedm)) error stop 'Softmax matrix input preservation'
            matrices=matrices+1; entries=entries+12
         end do
      end do
   end do
   print '(a,i0,a,i0,a,i0)', 'Rational/log-ratio softmax references: vectors=',vectors,', matrices=',matrices, &
      ', entries per function=',entries
   print '(a)', 'PASS stdlib-softmax-normalization-reference'
contains
   subroutine check(actual,expected)
      real(real64),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite softmax result'
      if(abs(actual-expected)>3.e-12_real64) error stop 'Independent normalization reference'
   end subroutine
end program
