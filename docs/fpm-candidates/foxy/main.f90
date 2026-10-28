! Intended example for the pinned FoXy API; not hosted-verified.
program xml_measurements
   use iso_fortran_env, only: dp => real64
   use foxy, only: xml_file
   implicit none
   type(xml_file) :: document
   character(*), parameter :: nl = new_line('a')
   character(*), parameter :: xml = '<measurements>'//nl// &
      '  <temperature unit="K">298.15</temperature>'//nl// &
      '  <pressure unit="Pa">101325</pressure>'//nl// &
      '  <length unit="m">0.25</length>'//nl// &
      '</measurements>'
   character(11), parameter :: names(3) = [character(11) :: 'temperature','pressure','length']
   character(2), parameter :: units(3) = [character(2) :: 'K','Pa','m']
   real(dp), parameter :: expected(3) = [298.15_dp,101325.0_dp,0.25_dp]
   character(:), allocatable :: text, unit_name
   real(dp) :: value
   integer :: file, i, id, status
   open(newunit=file,file='measurements.xml',status='replace',access='stream',form='unformatted')
   write(file) xml
   close(file)
   call document%parse(filename='measurements.xml')
   print '(a)', 'Measurements parsed from a file created by this program:'
   do i=1,3
      id = document%find(name=trim(names(i)))
      if (id==0) error stop 'Missing XML tag'
      text = document%content(trim(names(i)))
      unit_name = document%attribute(id,'unit')
      read(text,*,iostat=status) value
      if (status/=0) error stop 'Invalid numeric content'
      if (abs(value-expected(i))>1.e-9_dp .or. unit_name/=trim(units(i))) error stop 'XML value check'
      print '(a,1x,f12.3,1x,a)', trim(names(i)),value,unit_name
   end do
   print *, 'PASS foxy'
end program
