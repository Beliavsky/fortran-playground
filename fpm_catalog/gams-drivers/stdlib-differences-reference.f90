! Independent MIT consumer; see licenses/pca-ordering-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int32, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_math, only: diff
   implicit none
   real(real64),allocatable :: a(:),saved(:),work(:),output(:),expected(:)
   integer :: length,n,mode,i,j,k,c,calls
   calls=0
   do length=0,24
      allocate(a(length),saved(length))
      do i=1,length
         a(i)=real(i**3-2*i*i+mod(i,3),real64)/8
      end do
      saved=a
      do n=0,6
         do mode=1,2
            if(n==0.and.mode==2) cycle
            if(mode==1) then
               work=a
               output=diff(a,n=n)
            else
               work=[-2._real64,0.5_real64,a,3._real64]
               output=diff(a,n=n,prepend=[-2._real64,0.5_real64],append=[3._real64])
            end if
            allocate(expected(max(size(work)-n,0))); expected=0
            do i=1,size(expected)
               do j=0,n
                  c=1
                  do k=1,j
                     c=c*(n-k+1)/k
                  end do
                  expected(i)=expected(i)+(-1._real64)**(n-j)*c*work(i+j)
               end do
            end do
            if(size(output)/=size(expected)) error stop 'Difference output length'
            if(any(output/=expected)) error stop 'Independent binomial difference stencil'
            if(.not.all(ieee_is_finite(output))) error stop 'Nonfinite differences'
            if(any(a/=saved)) error stop 'Difference input preservation'
            deallocate(expected)
            calls=calls+1
         end do
      end do
      deallocate(a,saved)
   end do
   print '(a,i0)', 'Array differences versus independent binomial stencils, orders 0..6, with/without padding: ',calls
   print '(a)', 'PASS stdlib-differences-reference'
end program
