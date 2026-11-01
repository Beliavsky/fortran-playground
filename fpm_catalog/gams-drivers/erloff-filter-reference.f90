! Independent MIT consumer; see licenses/interop-ten-drivers-MIT.txt.
program main
   use erloff, only: error_list_t, fatal_t, module_t, procedure_t, message_type_t, OUT_OF_BOUNDS, INPUTS, size
   use iso_varying_string, only: char
   implicit none
   type(error_list_t) :: errors, snapshot, bounds, inputs_only
   character(24) :: message
   character(:), allocatable :: text, filtered
   integer :: i,j
   type(message_type_t) :: kind
   do i=1,48
      snapshot=errors
      kind=INPUTS
      if (mod(i,2)==0) kind=OUT_OF_BOUNDS
      write(message,'(a,i3.3,a)') '[diagnostic-',i,']'
      errors=errors%with_error_appended(fatal_t(kind,module_t('fixture'),procedure_t('check'),trim(message)))
      if (size(snapshot)/=i-1 .or. size(errors)/=i) error stop 'Immutable size'
      bounds=errors.ofType.OUT_OF_BOUNDS
      inputs_only=errors.ofType.INPUTS
      if (size(bounds)/=i/2 .or. size(inputs_only)/=(i+1)/2) error stop 'Filtered counts'
      text=char(errors%to_string())
      filtered=char(bounds%to_string())
      do j=1,i
         write(message,'(a,i3.3,a)') '[diagnostic-',j,']'
         if (index(text,trim(message))==0) error stop 'Lost diagnostic'
         if ((index(filtered,trim(message))>0) .neqv. (mod(j,2)==0)) error stop 'Filter contents'
      end do
      write(message,'(a,i3.3,a)') '[diagnostic-',i,']'
      if (index(char(snapshot%to_string()),trim(message))/=0) error stop 'Snapshot changed'
   end do
   print '(a)', '48 immutable append steps; exact parity-filter membership and snapshot preservation'
   print '(a)', 'PASS erloff-filter-reference'
end program
