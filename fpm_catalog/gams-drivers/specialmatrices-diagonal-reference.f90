! Independent API consumer; MIT: licenses/diagonal-response-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use SpecialMatrices,only:diagonal,solve,dense
   implicit none
   integer,parameter::sizes(*)=[1,2,7,32]
   real(wp),parameter::scales(*)=[-4.0_wp,0.125_wp,8.0_wp]
   type(diagonal)::matrix
   real(wp),allocatable::d(:),saved_d(:),b(:,:),saved_b(:,:),expected(:,:),x(:,:),v(:),before(:,:),after(:,:)
   real(wp)::value,worst,residual,worst_r,normalization
   integer::is,n,pattern,c,i,j,fixtures,calls,checks
   fixtures=0; calls=0; checks=0; worst=0; worst_r=0
   do is=1,size(sizes)
      n=sizes(is)
      allocate(d(n),saved_d(n),b(n,4),saved_b(n,4),expected(n,4))
      do pattern=1,3
         do j=1,size(scales)
            do i=1,n
               select case(pattern)
               case(1)
                  d(i)=i
               case(2)
                  d(i)=(-1.0_wp)**i*(1+mod(i,3))
               case(3)
                  d(i)=2.0_wp**(mod(i,7)-3)
               end select
            end do
            d=d*scales(j); saved_d=d
            matrix=diagonal(d)
            before=dense(matrix)
            do c=1,4
               do i=1,n
                  expected(i,c)=real(2*i-3*c,wp)/8
                  if (c==4) expected(i,c)=0
                  b(i,c)=d(i)*expected(i,c)
               end do
            end do
            saved_b=b
            x=solve(matrix,b)
            if (any(shape(x)/=[n,4]).or..not.all(ieee_is_finite(x))) error stop 'matrix solution'
            calls=calls+1
            do c=1,4
               v=solve(matrix,b(:,c))
               if (size(v)/=n.or..not.all(ieee_is_finite(v))) error stop 'vector solution'
               normalization=max(1.0_wp,maxval(abs(expected(:,c))))
               value=max(maxval(abs(x(:,c)-expected(:,c))),maxval(abs(v-expected(:,c))))/normalization
               if (value>2e-13_wp) error stop 'known diagonal solution'
               worst=max(worst,value)
               residual=0
               do i=1,n
                  normalization=max(1.0_wp,abs(b(i,c)),abs(d(i)*expected(i,c)))
                  residual=max(residual,abs(d(i)*x(i,c)-b(i,c))/normalization, &
                     abs(d(i)*v(i)-b(i,c))/normalization)
               end do
               if (residual>2e-13_wp) error stop 'diagonal residual'
               worst_r=max(worst_r,residual)
               calls=calls+1; checks=checks+2*n
            end do
            after=dense(matrix)
            if (any(after/=before).or.any(d/=saved_d).or.any(b/=saved_b)) error stop 'changed input'
            fixtures=fixtures+1
         end do
      end do
      deallocate(d,saved_d,b,saved_b,expected)
   end do
   if (fixtures/=36.or.calls/=180.or.checks/=3024) error stop 'accounting'
   print '(a,i0,a,i0)', 'Nonsingular diagonal fixtures: ',fixtures,'; solve calls: ',calls
   print '(a,i0)', 'Known solution coordinate checks: ',checks
   print '(a)', 'One four-column RHS and four vector RHS calls; signed diagonals and zero RHS.'
   print '(a,es12.4)', 'Maximum normalized solution error: ',worst
   print '(a,es12.4)', 'Maximum normalized scalar residual: ',worst_r
   print '(a)', 'PASS specialmatrices-diagonal-reference'
end program
