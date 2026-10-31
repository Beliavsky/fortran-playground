! Author API patterns adapted on 2026-10-30: independent direct-sum convolution checks.
! MIT License
! 
! Copyright (c) 2023-2026 Jason Christopherson
! 
! Permission is hereby granted, free of charge, to any person obtaining a copy
! of this software and associated documentation files (the "Software"), to deal
! in the Software without restriction, including without limitation the rights
! to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
! copies of the Software, and to permit persons to whom the Software is
! furnished to do so, subject to the following conditions:
! 
! The above copyright notice and this permission notice shall be included in all
! copies or substantial portions of the Software.
! 
! THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
! IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
! FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
! AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
! LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
! OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
! SOFTWARE.
module direct_convolution
   use iso_fortran_env, only: wp=>real64,sp=>real32
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
contains
   function full_reference(x,h) result(y)
      real(wp), intent(in) :: x(:),h(:)
      real(wp) :: y(size(x)+size(h)-1)
      integer :: i,j
      y=0._wp
      do j=1,size(h)
         do i=1,size(x)
            y(i+j-1)=y(i+j-1)+x(i)*h(j)
         end do
      end do
   end function
   subroutine check(y,reference,tolerance,error)
      real(wp), intent(in) :: y(:),reference(:),tolerance
      real(wp), intent(out) :: error
      if (size(y)/=size(reference)) error stop 'convolution output length mismatch'
      if (.not.all(ieee_is_finite(y))) error stop 'nonfinite convolution output'
      error=maxval(abs(y-reference))/max(1._wp,maxval(abs(reference)))
      if (error>tolerance) error stop 'direct convolution reference mismatch'
   end subroutine
end module
program checked_convolution
   use direct_convolution
   use spectrum, only: convolve,SPCTRM_CENTRAL_CONVOLUTION
   implicit none
   integer, parameter :: n=37,lengths(8)=[1,2,3,4,5,8,16,17]
   real(wp) :: x(n),first_error,second_error,third_error,fourth_error,mass_error
   real(wp), allocatable :: h(:),full(:),result(:)

   integer :: signal,choice,m,i,first
   do signal=1,2
      if (signal==1) then
         x=0._wp;x(10)=1._wp
      else
         do i=1,n
            x(i)=sin(0.2_wp*i)+(-1._wp)**i*0.1_wp*i
         end do
      end if
      do choice=1,size(lengths)
         m=lengths(choice)
         allocate(h(m))
         do i=1,m
            h(i)=(-1._wp)**i/real(i+1,wp)
         end do
         if (m==1) h=1._wp
         full=full_reference(x,h)
         result=convolve(x,h)
         call check(result,full,1.e-11_wp,first_error)
         mass_error=abs(sum(result)-sum(x)*sum(h))/max(1._wp,abs(sum(x)*sum(h)))
         if (mass_error>1.e-11_wp) error stop 'full convolution sum identity'
         result=convolve(h,x)
         call check(result,full,1.e-11_wp,second_error)
         ! The central convention at this pin starts at floor(m/2)+1, including even kernels.
         first=m/2+1
         result=convolve(x,h,SPCTRM_CENTRAL_CONVOLUTION)
         call check(result,full(first:first+n-1),1.e-11_wp,third_error)
         result=convolve(h,x,SPCTRM_CENTRAL_CONVOLUTION)
         call check(result,full(first:first+n-1),1.e-11_wp,fourth_error)
         print '(a,i0,a,i0,a,2i4)', 'Signal ',signal,' kernel ',m,' full/central lengths:',size(full),size(result)
         print '(a,5es12.3)', 'Scaled full / swapped / central / swapped central / sum errors:', &
            first_error,second_error,third_error,fourth_error,mass_error

         deallocate(h)
      end do
   end do
   print '(a)', 'PASS spectrum-convolution-reference'
end program
