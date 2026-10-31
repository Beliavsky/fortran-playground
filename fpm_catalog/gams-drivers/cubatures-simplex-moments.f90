! Adapted author API patterns; analytic integral and moment checks.
! MIT License
! 
! Copyright (c) 2025-2026 Will Klausler
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
program checked_cubature_rules
   use iso_fortran_env, only: wp=>real64
   use cubatures, only: cubature,CUB_TRI,CUB_TET,CUB_QUA
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: elements(3)=[CUB_TRI,CUB_TET,CUB_QUA],degrees(3)=[5,4,5]
   character(13), parameter :: names(3)=['triangle     ','tetrahedron  ','quadrilateral']
   type(cubature) :: q
   real(wp) :: exact,answer,error,max_error
   real(wp), allocatable :: f(:)
   integer :: shape,a,b,c,p,count
   do shape=1,3
      p=degrees(shape)
      q=cubature(elements(shape),p)
      if (.not.q%is_valid()) error stop 'invalid cubature rule'
      if (.not.all(ieee_is_finite(q%weights)).or..not.all(ieee_is_finite(q%abscissae))) &
         error stop 'nonfinite cubature data'
      if (any(q%weights<=0._wp)) error stop 'nonpositive cubature weights'
      if (shape<3) then
         if (any(q%abscissae<=0._wp).or.any(sum(q%abscissae,dim=1)>=1._wp)) error stop 'nodes outside simplex'
      else
         if (any(abs(q%abscissae)>=1._wp)) error stop 'nodes outside square'
      end if
      max_error=0._wp;count=0
      do c=0,p
         do b=0,p
            do a=0,p
               if (q%dim==2.and.c>0) cycle
               if (shape<3.and.a+b+c>p) cycle
               f=q%abscissae(1,:)**a*q%abscissae(2,:)**b
               if (q%dim==3) f=f*q%abscissae(3,:)**c
               if (shape<3) then
                  exact=factorial(a)*factorial(b)*factorial(c)/factorial(a+b+c+q%dim)
               else
                  exact=line_moment(a)*line_moment(b)
               end if
               answer=sum(q%weights*f)
               error=abs(answer-exact)/max(1._wp,abs(exact))
               if (error>1.e-12_wp) error stop 'analytic monomial integral mismatch'
               max_error=max(max_error,error);count=count+1
            end do
         end do
      end do
      print '(a,a,i0,a,i0,a,i0)',trim(names(shape)),' degree=',p,' points=',q%npoints,' moments=',count
      print '(a,es12.4)', 'Maximum scaled moment error:',max_error
      call q%destroy()
   end do
   print '(a)', 'PASS cubatures-simplex-moments'
contains
   pure real(wp) function factorial(n) result(value)
      integer, intent(in) :: n
      integer :: i
      value=1._wp
      do i=2,n
         value=value*i
      end do
   end function
   pure real(wp) function line_moment(k) result(value)
      integer, intent(in) :: k
      value=0._wp
      if (mod(k,2)==0) value=2._wp/(k+1)
   end function
end program
