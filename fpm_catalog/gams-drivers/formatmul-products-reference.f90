! Independent API consumer; see licenses/products-partitions-drivers-MIT.txt.
program checked_matrix_products
   use kinds, only: rk
   use formatmul, only: matmul
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: dims(3,6)=reshape([1,1,1,1,3,2,2,1,4,2,3,5,5,4,3,7,5,9],[3,6])
   character(2), parameter :: methods(4)=['m1','m2','m3','m4']
   real(rk), allocatable :: a(:,:),b(:,:),saved_a(:,:),saved_b(:,:),expected(:,:),scale(:,:),c(:,:),v(:)
   real(rk) :: worst=0
   integer :: fixture,family,method,branch,m,k,n,i,j,l,products=0,entries=0
   do fixture=1,6
      m=dims(1,fixture); k=dims(2,fixture); n=dims(3,fixture)
      allocate(a(m,k),b(k,n),saved_a(m,k),saved_b(k,n),expected(m,n),scale(m,n))
      do family=1,3
         do j=1,k
            do i=1,m
               select case(family)
               case(1)
                  a(i,j)=0
               case(2)
                  a(i,j)=real(modulo(3*i+7*j,11)-5,rk)/4
               case(3)
                  a(i,j)=sin(real(2*i+3*j,rk))+(-1.0_rk)**i/4
               end select
            end do
         end do
         do j=1,n
            do i=1,k
               select case(family)
               case(1)
                  b(i,j)=real(i-j,rk)
               case(2)
                  b(i,j)=real(modulo(5*i+2*j,13)-6,rk)/8
               case(3)
                  b(i,j)=cos(real(3*i-j,rk))-real(i,rk)/(j+1)
               end select
            end do
         end do
         saved_a=a; saved_b=b; expected=0; scale=0
         do j=1,n
            do i=1,m
               do l=1,k
                  expected(i,j)=expected(i,j)+a(i,l)*b(l,j)
                  scale(i,j)=scale(i,j)+abs(a(i,l)*b(l,j))
               end do
            end do
         end do
         do method=1,4
            do branch=1,5
               select case(branch)
               case(1)
                  c=matmul(a,b,option=methods(method))
               case(2)
                  c=matmul(a,b,transA=.false.,transB=.false.,option=methods(method))
               case(3)
                  c=matmul(transpose(a),b,transA=.true.,transB=.false.,option=methods(method))
               case(4)
                  c=matmul(a,transpose(b),transA=.false.,transB=.true.,option=methods(method))
               case(5)
                  c=matmul(transpose(a),transpose(b),transA=.true.,transB=.true.,option=methods(method))
               end select
               if (any(shape(c)/=[m,n])) error stop 'matrix product shape'
               call compare(reshape(c,[m*n]),reshape(expected,[m*n]),reshape(scale,[m*n]))
            end do
            do branch=1,3
               select case(branch)
               case(1)
                  v=matmul(a,b(:,1),option=methods(method))
               case(2)
                  v=matmul(a,b(:,1),transA=.false.,option=methods(method))
               case(3)
                  v=matmul(transpose(a),b(:,1),transA=.true.,option=methods(method))
               end select
               if (size(v)/=m) error stop 'matrix vector shape'
               call compare(v,expected(:,1),scale(:,1))
            end do
            if (any(a/=saved_a).or.any(b/=saved_b)) error stop 'product inputs changed'
         end do
      end do
      deallocate(a,b,saved_a,saved_b,expected,scale)
   end do
   print '(a,i0)', 'Matrix/matrix-vector calls: ',products
   print '(a,i0)', 'Independent scalar product entries: ',entries
   print '(a,es12.4)', 'Maximum sum-absolute-product scaled error: ',worst
   print '(a)', 'PASS formatmul-products-reference'
contains
   subroutine compare(actual,reference,sumabs)
      real(rk), intent(in) :: actual(:),reference(:),sumabs(:)
      real(rk) :: error
      if (.not.all(ieee_is_finite(actual))) error stop 'nonfinite product'
      error=maxval(abs(actual-reference)/(1+sumabs)); worst=max(worst,error)
      if (error>128*epsilon(1.0_rk)*k) error stop 'independent scalar product'
      if (family<3.and.any(actual/=reference)) error stop 'exact dyadic product'
      products=products+1; entries=entries+size(actual)
   end subroutine compare
end program checked_matrix_products
