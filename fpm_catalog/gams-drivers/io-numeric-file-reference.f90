! Independent API consumer; MIT: licenses/io-bounds-drivers-MIT.txt.
program numeric_file_reference
   use, intrinsic :: iso_fortran_env, only: dp => real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use io_fortran_lib, only: to_file,from_file
   implicit none
   integer, parameter :: dimensions(2,4) = reshape([1,1,2,3,4,2,3,4],[2,4])
   character, parameter :: separators(*) = [',',';']
   real(dp), allocatable :: values(:,:),loaded(:,:),row(:)
   real(dp) :: native_expected(4,3),max_error
   character(512) :: message
   character(2048) :: line
   integer :: unit,status,shape_case,separator,i,j,rows,cols,cases,k
   max_error = 0._dp
   cases = 0
   do shape_case = 1,4
      rows = dimensions(1,shape_case)
      cols = dimensions(2,shape_case)
      allocate(values(rows,cols),row(cols))
      do j = 1,cols
         do i = 1,rows
            values(i,j) = real(10*i-7*j,dp)/8
         end do
      end do
      values(1,1) = 0._dp
      do separator = 1,2
         call to_file(values,'gams-io-output.csv',delim=separators(separator),fmt='e',stat=status,errmsg=message)
         if (status /= 0) error stop 'library numeric write status'
         ! Independent native reader verifies row orientation, delimiter and values.
         open(newunit=unit,file='gams-io-output.csv',status='old',action='read',iostat=status)
         if (status /= 0) error stop 'native output open'
         do i = 1,rows
            read(unit,'(a)',iostat=status) line
            if (status /= 0) error stop 'missing numeric output row'
            if (count([(line(k:k)==separators(separator),k=1,len_trim(line))]) /= cols-1) &
               error stop 'output column delimiter count'
            do k = 1,len_trim(line)
               if (line(k:k) == separators(separator)) line(k:k) = ' '
            end do
            read(line,*,iostat=status) row
            if (status /= 0) error stop 'native output numeric parse'
            call compare(row,values(i,:))
         end do
         read(unit,'(a)',iostat=status) line
         if (status >= 0) error stop 'extra numeric output row'
         close(unit)
         call from_file('gams-io-output.csv',into=loaded,delim=separators(separator),stat=status,errmsg=message)
         if (status /= 0) error stop 'library numeric read status'
         if (.not. allocated(loaded)) error stop 'missing numeric read allocation'
         if (any(shape(loaded) /= shape(values))) error stop 'numeric read dimensions'
         do i = 1,rows
            call compare(loaded(i,:),values(i,:))
         end do
         deallocate(loaded)
         open(newunit=unit,file='gams-io-output.csv',status='old')
         close(unit,status='delete')
         cases = cases+1
      end do
      deallocate(values,row)
   end do
   ! This fixture is written without the library, so reader/writer mistakes cannot cancel.
   native_expected = reshape([1.25_dp,0._dp,-8._dp,.125_dp, &
      -2.5_dp,4._dp,.5_dp,-.25_dp, 0._dp,-.75_dp,16._dp,2._dp],[4,3])
   open(newunit=unit,file='gams-io-native.csv',status='replace',action='write',iostat=status)
   if (status /= 0) error stop 'native CSV creation'
   write(unit,'(a)') '1.25,-2.5,0.0','0.0,4.0,-0.75','-8.0,0.5,16.0','0.125,-0.25,2.0'
   close(unit)
   call from_file('gams-io-native.csv',into=loaded,delim=',',stat=status,errmsg=message)
   if (status /= 0) error stop 'native CSV library read'
   if (.not. allocated(loaded)) error stop 'native CSV allocation'
   if (any(shape(loaded) /= [4,3])) error stop 'native CSV shape'
   do i = 1,4
      call compare(loaded(i,:),native_expected(i,:))
   end do
   deallocate(loaded)
   open(newunit=unit,file='gams-io-native.csv',status='old')
   close(unit,status='delete')
   call from_file('gams-io-missing.csv',into=loaded,stat=status,errmsg=message)
   if (status == 0 .or. len_trim(message) == 0) error stop 'missing-file error status/message'
   if (cases /= 8) error stop 'numeric file fixture count'
   print '(a)', '8 real64 matrix files: four shapes, comma/semicolon delimiters, independent native parsing.'
   print '(a)', 'Hand-written CSV, row/column layout, library round trips and missing-file diagnostics checked.'
   print '(a,es12.4)', 'Maximum normalized numeric file error: ',max_error
   print '(a)', 'PASS io-numeric-file-reference'
contains
   subroutine compare(actual,reference)
      real(dp), intent(in) :: actual(:),reference(:)
      real(dp) :: error
      if (.not. all(ieee_is_finite(actual))) error stop 'nonfinite numeric file data'
      error = maxval(abs(actual-reference)/max(1._dp,abs(reference)))
      max_error = max(max_error,error)
      if (error > 5.e-14_dp) error stop 'independent numeric file reference'
   end subroutine compare
end program numeric_file_reference
