program demo_sparse
   use sparse_fortran, only: sparse_coo,sparse_csr
   use iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n=8
   type(sparse_coo) :: coo
   type(sparse_csr) :: csr
   real(real64) :: dense(n,n),x(n),expected(n),from_coo(n),from_csr(n)
   integer :: i
   dense = 0
   do i=1,n
      dense(i,i) = 2
      if (i<n) then
         dense(i,i+1) = -1
         dense(i+1,i) = -1
      end if
   end do
   x = [(real(i*(n+1-i),real64),i=1,n)]
   ! This discrete parabola has second difference -2, including the zero boundaries.
   expected = 2.0_real64
   call coo%sparse_init(dense)
   call csr%sparse_init(dense)
   from_coo = coo%sparse_product(x)
   from_csr = csr%sparse_product(x)
   if (.not. all(ieee_is_finite(from_coo))) error stop 'Nonfinite COO product'
   if (.not. all(ieee_is_finite(from_csr))) error stop 'Nonfinite CSR product'
   if (maxval(abs(from_coo-expected))>1e-12_real64) error stop 'Wrong COO product'
   if (maxval(abs(from_csr-expected))>1e-12_real64) error stop 'Wrong CSR product'
   if (maxval(abs(matmul(dense,x)-expected))>1e-12_real64) error stop 'Wrong reference'
   print '(a,8f7.2)', 'Input vector: ',x
   print '(a,8f7.2)', 'COO product:  ',from_coo
   print '(a,8f7.2)', 'CSR product:  ',from_csr
   print '(a)', 'PASS sparse_fortran'
end program
