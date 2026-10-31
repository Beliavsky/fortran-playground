! Independent API consumer; MIT: licenses/storage-fourier-geometry-drivers-MIT.txt.
program storage_reference
   use fsparse, only: COO_dp, CSR_dp, dense2coo, coo2dense, coo2csr, csr2coo
   use fsparse_constants, only: dp
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(dp) :: a(5,4), zero(3,2), full(2,3), scalar(1,1)
   integer :: i, j
   a = 0._dp
   a(2,1) = -2._dp
   a(2,4) = .5_dp
   a(4,2) = 3._dp
   a(4,4) = -4._dp
   zero = 0._dp
   do j = 1, 3
      do i = 1, 2
         full(i,j) = real(2*i+3*j,dp)/2
      end do
   end do
   scalar = -7._dp
   call check(a)
   call check(transpose(a))
   call check(zero)
   call check(full)
   call check(scalar)
   print '(a)', 'PASS fsparse-storage-reference'
contains
   subroutine check(dense)
      real(dp), intent(in) :: dense(:,:)
      type(COO_dp) :: coo, returned
      type(CSR_dp) :: csr
      real(dp) :: reconstructed(size(dense,1),size(dense,2)), restored(size(dense,1),size(dense,2))
      integer :: i, j, k, entry, nonzeros, expected_ptr(size(dense,1)+1)
      ! Fixtures use exact moderate dyadic values: no threshold or subnormal cases.
      nonzeros = count(dense /= 0._dp)
      call dense2coo(dense,coo)
      call check_coo(coo,dense)
      call coo2csr(coo,csr)
      if (csr%nrows /= size(dense,1) .or. csr%ncols /= size(dense,2)) error stop 'CSR dimensions'
      if (csr%nnz /= nonzeros .or. csr%base /= 1) error stop 'CSR count or base'
      if (size(csr%rowptr) /= size(dense,1)+1) error stop 'CSR row pointer length'
      if (size(csr%col) /= nonzeros .or. size(csr%data) /= nonzeros) error stop 'CSR array lengths'
      expected_ptr(1) = 1
      do i = 1, size(dense,1)
         expected_ptr(i+1) = expected_ptr(i)+count(dense(i,:) /= 0._dp)
      end do
      if (any(csr%rowptr /= expected_ptr)) error stop 'independent CSR row counts'
      if (.not. all(ieee_is_finite(csr%data))) error stop 'nonfinite CSR data'
      reconstructed = 0._dp
      k = 0
      do i = 1, size(dense,1)
         do j = 1, size(dense,2)
            if (dense(i,j) == 0._dp) cycle
            k = k+1
            if (csr%col(k) /= j .or. csr%data(k) /= dense(i,j)) error stop 'CSR column/value reference'
         end do
         do entry = csr%rowptr(i), csr%rowptr(i+1)-1
            j = csr%col(entry)
            if (j < 1 .or. j > size(dense,2)) error stop 'CSR column range'
            reconstructed(i,j) = csr%data(entry)
         end do
      end do
      if (any(reconstructed /= dense)) error stop 'independent CSR reconstruction'
      call csr2coo(csr,returned)
      call check_coo(returned,dense)
      ! coo2dense writes stored entries only; callers must initialize omitted zeros.
      restored = 0._dp
      call coo2dense(coo,restored)
      if (any(restored /= dense)) error stop 'COO dense restoration'
      restored = 0._dp
      call coo2dense(returned,restored)
      if (any(restored /= dense)) error stop 'CSR to COO dense restoration'
      print '(a,i0,a,i0,a,i0)', 'Dense/COO/CSR checked: ',size(dense,1),' x ',size(dense,2),' nnz=',nonzeros
   end subroutine check

   subroutine check_coo(coo,dense)
      type(COO_dp), intent(in) :: coo
      real(dp), intent(in) :: dense(:,:)
      integer :: i, j, k, nonzeros
      nonzeros = count(dense /= 0._dp)
      if (coo%nrows /= size(dense,1) .or. coo%ncols /= size(dense,2)) error stop 'COO dimensions'
      if (coo%nnz /= nonzeros .or. coo%base /= 1) error stop 'COO count or base'
      if (any(shape(coo%index) /= [2,nonzeros])) error stop 'COO coordinate shape'
      if (size(coo%data) /= nonzeros) error stop 'COO value count'
      if (.not. all(ieee_is_finite(coo%data))) error stop 'nonfinite COO data'
      k = 0
      do i = 1, size(dense,1)
         do j = 1, size(dense,2)
            if (dense(i,j) == 0._dp) cycle
            k = k+1
            if (any(coo%index(:,k) /= [i,j])) error stop 'independent COO coordinates'
            if (coo%data(k) /= dense(i,j)) error stop 'independent COO value'
         end do
      end do
   end subroutine check_coo
end program storage_reference
