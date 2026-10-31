! Independent API consumer; MIT: licenses/higher-ad-drivers-MIT.txt.
program main
   use config_mod,only:prec,max_order_dualzn
   use dualzn_mod
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
   real(prec),parameter::reals(*)=[-1.0_prec,-0.25_prec,0.0_prec,0.5_prec,1.0_prec]
   real(prec),parameter::imags(*)=[-0.5_prec,0.0_prec,0.25_prec]
   real(prec),parameter::a_values(*)=[0.5_prec,1.0_prec,2.0_prec],b_values(*)=[-2.0_prec,0.5_prec,1.0_prec]
   integer,parameter::coeff(0:5)=[1,3,0,-2,0,1]
   type(dualzn)::x,y
   complex(prec)::z,expected,u,polynomial
   real(prec)::a,b,error,worst
   integer::ir,ii,order,k,pair,j,d,expressions,checks,transcendental,composed,algebraic
   if (max_order_dualzn<5.or.precision(1.0_prec)<15) error stop 'configured order/precision'
   expressions=0; checks=0; transcendental=0; composed=0; algebraic=0; worst=0
   do ir=1,size(reals)
      do ii=1,size(imags)
         z=cmplx(reals(ir),imags(ii),prec)
         do order=0,5
            x=xto_dzn(z,order)
            if (order>=1) x%f(1)=1
            do pair=1,3
               a=a_values(pair); b=b_values(pair)
               y=exp(a*x)+sin(b*x)
               if (y%ord/=order) error stop 'result derivative order'
               expressions=expressions+1
               do k=0,order
                  select case(modulo(k,4))
                  case(0)
                     expected=b**k*sin(b*z)
                  case(1)
                     expected=b**k*cos(b*z)
                  case(2)
                     expected=-b**k*sin(b*z)
                  case(3)
                     expected=-b**k*cos(b*z)
                  end select
                  expected=expected+a**k*exp(a*z)
                  call check(y%f(k),expected)
                  transcendental=transcendental+1
               end do
            end do
            y=exp(x*x+x)
            if (y%ord/=order) error stop 'composition derivative order'
            expressions=expressions+1
            u=2*z+1
            do k=0,order
               polynomial=0
               do j=0,k/2
                  polynomial=polynomial+real(factorial(k)/(factorial(j)*factorial(k-2*j)),prec)*u**(k-2*j)
               end do
               expected=exp(z*z+z)*polynomial
               call check(y%f(k),expected)
               composed=composed+1
            end do
            y=x*x*x*x*x-2*x*x*x+3*x+1
            if (y%ord/=order) error stop 'polynomial derivative order'
            expressions=expressions+1
            do k=0,order
               expected=0
               do d=k,5
                  expected=expected+real(coeff(d)*factorial(d)/factorial(d-k),prec)*z**(d-k)
               end do
               call check(y%f(k),expected)
               algebraic=algebraic+1
            end do
         end do
      end do
   end do
   if (expressions/=450.or.checks/=1575.or.transcendental/=945.or.composed/=315.or.algebraic/=315) &
      error stop 'fixture accounting'
   print '(a,i0,a,i0)', 'Dual expressions at 15 real/complex points and requested orders 0..5: ',expressions, &
      '; derivative references: ',checks
   print '(a,3i6)', 'Scaled exp/sin / composed exp / polynomial derivatives: ',transcendental,composed,algebraic
   print '(a,es12.4)', 'Maximum normalized complex derivative error: ',worst
   print '(a)', 'PASS dnaoad-higher-reference'
contains
   integer function factorial(n) result(value)
      integer,intent(in)::n
      integer::i
      value=1
      do i=2,n
         value=value*i
      end do
   end function factorial
   subroutine check(actual,reference)
      complex(prec),intent(in)::actual,reference
      if (.not.ieee_is_finite(real(actual,prec)).or..not.ieee_is_finite(aimag(actual))) &
         error stop 'nonfinite complex derivative'
      error=abs(actual-reference)/max(1.0_prec,abs(reference))
      if (error>2e-11_prec) error stop 'closed-form complex derivative'
      worst=max(worst,error); checks=checks+1
   end subroutine check
end program main
