! Independent checked API consumer; see licenses/neighbors-sparse-drivers-MIT.txt.
program checked_sparse_matvec
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use sparse_fortran, only: sparse_coo,sparse_csr
   implicit none
   integer, parameter :: sizes(5)=[1,2,3,8,17]
   integer :: i,j,pattern,order,fixtures=0,products=0,entries=0
   do i=1,size(sizes)
      do j=1,size(sizes)
         do pattern=1,5
            do order=1,2
               call fixture(sizes(i),sizes(j),pattern,order)
            end do
         end do
      end do
   end do
   print '(a,i0)', 'Matrix/order fixtures: ',fixtures
   print '(a,i0)', 'COO/CSR products: ',products
   print '(a,i0)', 'Checked result entries: ',entries
   print '(a)', 'PASS sparse-matvec-reference'
contains
   subroutine fixture(m,n,pattern,order)
      integer, intent(in) :: m,n,pattern,order
      type(sparse_coo) :: coo
      type(sparse_csr) :: csr
      real(real64) :: a(m,n),saved(m,n)
      real(real64), allocatable :: x(:),ref(:),y(:),z(:)
      integer :: i,j,r,nin,nout
      character :: storage
      a=0
      do j=1,n
         do i=1,m
            select case(pattern)
            case(1) ! Entirely zero, including empty rows/columns.
            case(2)
               if (i==j) a(i,j)=real(2*i-3,real64)/4
            case(3)
               if (i==j) a(i,j)=2
               if (abs(i-j)==1) a(i,j)=-1
            case(4)
               if (i/=max(1,m/2).and.j/=max(1,n/2).and.mod(3*i+5*j,4)==0) &
                  a(i,j)=real(mod(11*i+7*j,19)-9,real64)/8
            case(5)
               a(i,j)=real(mod(11*i+7*j,19)-9,real64)/8
            end select
         end do
      end do
      saved=a
      storage='C'; nin=n; nout=m
      if (order==2) then
         storage='F'; nin=m; nout=n
      end if
      ! This API's non-C order computes the transpose product, not A*x.
      call coo%sparse_init(a,order=storage)
      call csr%sparse_init(a,order=storage)
      if (any(a/=saved)) error stop 'matrix input changed'
      allocate(x(nin),ref(nout))
      do r=1,3
         do i=1,nin
            select case(r)
            case(1)
               x(i)=1
            case(2)
               x(i)=real((-1)**i*i,real64)/8
            case(3)
               x(i)=real(i*(nin+1-i),real64)/4
            end select
         end do
         ref=0
         ! Scalar dense oracle; no use of either sparse representation.
         do j=1,n
            do i=1,m
               if (order==1) then
                  ref(i)=ref(i)+saved(i,j)*x(j)
               else
                  ref(j)=ref(j)+saved(i,j)*x(i)
               end if
            end do
         end do
         y=coo%sparse_product(x); z=csr%sparse_product(x)
         if (size(y)/=nout.or.size(z)/=nout) error stop 'result shape'
         if (.not.all(ieee_is_finite(y)).or..not.all(ieee_is_finite(z))) error stop 'nonfinite product'
         ! Binary fractions and small integer sums make exact comparison appropriate.
         if (any(y/=ref).or.any(z/=ref)) error stop 'scalar reference mismatch'
         products=products+2; entries=entries+2*nout
      end do
      fixtures=fixtures+1
   end subroutine fixture
end program checked_sparse_matvec
