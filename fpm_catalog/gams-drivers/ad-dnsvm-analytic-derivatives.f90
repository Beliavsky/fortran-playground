! Adapted author API patterns; shared analytic derivative checks.
! MIT License
! 
! Copyright (c) 2022 lauvergn
! Copyright (c) 2022 David Lauvergnat (author example)
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
program checked_differentiation
   use QDUtil_m, only: Rkind
   use ADdnSVM_m
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(Rkind), parameter :: points(4)=[-0.5_Rkind,0._Rkind,0.5_Rkind,1._Rkind]
   type(dnS_t) :: x,y
   real(Rkind) :: t,reference(0:3),answer(0:3),scaled_error,max_error
   real(Rkind), allocatable :: d1(:),d2(:,:),d3(:,:,:)
   integer :: i,order
   max_error=0._Rkind
   do i=1,size(points)
      t=points(i)
      x=Variable(Val=t,nVar=1,iVar=1,nderiv=3)
      y=exp(x)*sin(x)
      d1=get_d1(y);d2=get_d2(y);d3=get_d3(y)
      if (size(d1)/=1.or.size(d2)/=1.or.size(d3)/=1) error stop 'unexpected derivative tensor shape'
      answer=[get_d0(y),d1(1),d2(1,1),d3(1,1,1)]
      reference=[exp(t)*sin(t),exp(t)*(sin(t)+cos(t)),2._Rkind*exp(t)*cos(t), &
                 2._Rkind*exp(t)*(cos(t)-sin(t))]
      if (.not.all(ieee_is_finite(answer))) error stop 'nonfinite automatic derivative'
      do order=0,3
         scaled_error=abs(answer(order)-reference(order))/max(1._Rkind,abs(reference(order)))
         if (scaled_error>5.e-14_Rkind) error stop 'analytic derivative mismatch'
         max_error=max(max_error,scaled_error)
      end do
      print '(a,f5.1,a,4es15.6)', 'x=',t,' value and derivatives 1..3:',answer
   end do
   print '(a,es12.4)', 'Maximum scaled analytic error: ',max_error
   print '(a)', 'PASS ad-dnsvm-analytic-derivatives'
end program
