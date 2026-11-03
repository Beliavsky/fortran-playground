! Independent MIT consumer; see licenses/fortranlib-tables-drivers-MIT.txt.
module reference_model
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
contains
   elemental function parameter(mode,k) result(p)
      integer,intent(in)::mode,k
      real(wp)::p
      real(wp),parameter::powers(5)=[-2._wp,-1._wp,0._wp,0.5_wp,2._wp]
      select case(mode)
      case(0)
         p=real(k-2,wp)
      case(1)
         p=real(k-2,wp)/4
      case(2)
         p=real(k-2,wp)/2
      case(3)
         p=powers(k)
      end select
   end function
   elemental function field(x,mode,p) result(y)
      real(wp),intent(in)::x,p
      integer,intent(in)::mode
      real(wp)::y
      select case(mode)
      case(0)
         y=2+p*x
      case(1)
         y=3*exp(p*x)
      case(2)
         y=2+p*log(x)
      case(3)
         y=3*x**p
      end select
   end function
   elemental function primitive(x,mode,p) result(y)
      real(wp),intent(in)::x,p
      integer,intent(in)::mode
      real(wp)::y
      select case(mode)
      case(0)
         y=2*x+p*x*x/2
      case(1)
         if(p==0) then
            y=3*x
         else
            y=3*exp(p*x)/p
         end if
      case(2)
         y=2*x+p*(x*log(x)-x)
      case(3)
         if(p==-1) then
            y=3*log(x)
         else
            y=3*x**(p+1)/(p+1)
         end if
      end select
   end function
   subroutine check(actual,expected)
      real(wp),intent(in)::actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-11_wp*max(1._wp,abs(expected))) then
         print *, 'Actual, expected:',actual,expected
         error stop 'Independent analytic reference'
      end if
   end subroutine
end module
program main
   use reference_model
   use lib_array,only:histogram1d,histogram2d
   implicit none
   real(wp)::points(11),weights(11),hx(4),hy(4),expected(4),xx(121),yy(121)
   real(wp)::counts(4,4),reference(4,4),weight
   logical::mask(11),mask2(121)
   integer::i,j,k,l,variant,weighted,n
   points=[(real(i-6,wp)/4,i=1,11)];weights=[(1+real(i,wp)/4,i=1,11)]
   do variant=1,3
      mask=.true.
      if(variant==2)mask=[(modulo(i,2)==1,i=1,11)]
      if(variant==3)mask=.false.
      do weighted=0,1
         expected=0
         do i=1,11
            if(.not.mask(i)) cycle
            weight=1;if(weighted==1)weight=weights(i)
            do j=1,4
               if(in_bin(points(i),j))expected(j)=expected(j)+weight
            end do
         end do
         if(weighted==0)then
            call histogram1d(points,-1._wp,1._wp,4,hx,hy,mask=mask)
         else
            call histogram1d(points,-1._wp,1._wp,4,hx,hy,mask=mask,weights=weights)
         end if
         if(any(hy/=expected)) error stop 'Exact count or weighted sum'
         do j=1,4
            call check(hx(j),-1._wp+(real(j,wp)-0.5_wp)/2)
         end do
      end do
   end do
   n=0
   do i=1,11
      do j=1,11
         n=n+1;xx(n)=points(i);yy(n)=points(j)
      end do
   end do
   do variant=1,3
      mask2=.true.
      if(variant==2)mask2=[(modulo(i,3)==1,i=1,121)]
      if(variant==3)mask2=.false.
      reference=0
      do i=1,121
         if(.not.mask2(i))cycle
         do j=1,4
            do k=1,4
               if(in_bin(xx(i),j).and.in_bin(yy(i),k))reference(j,k)=reference(j,k)+1
            end do
         end do
      end do
      call histogram2d(121,xx,yy,-1._wp,1._wp,-1._wp,1._wp,4,4,counts,mask_in=mask2)
      if(any(counts/=reference))error stop 'Exact two-dimensional bin count'
   end do
   print '(a)', '6 one-dimensional histograms and 3 two-dimensional histograms independently checked.'
   print '(a)', 'PASS fortranlib-masked-histograms-reference'
contains
   logical function in_bin(value,bin)
      real(wp),intent(in)::value
      integer,intent(in)::bin
      real(wp)::left,right
      left=-1+real(bin-1,wp)/2;right=left+0.5_wp
      in_bin=value>=left.and.value<right
      if(bin==4.and.value==1)in_bin=.true.
   end function
end program
