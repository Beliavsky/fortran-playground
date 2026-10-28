program main
   use iso_fortran_env, only: real64
   use str2real_m, only: str2real
   implicit none
   character(12), parameter :: text(3)=[character(12)::'12.34E1','-2.5e-2','6.022E3']
   real(real64), parameter :: expected(3)=[123.4_real64,-.025_real64,6022._real64]
   real(real64) :: parsed
   integer :: i
   ! Supply valid numeric strings; this parser does not validate malformed input.
   do i=1,size(text)
      parsed=str2real(trim(text(i)))
      if (abs(parsed-expected(i))>1e-12_real64*max(1._real64,abs(expected(i)))) error stop
      print '(a,1x,f14.6)', trim(text(i))//' ->',parsed
   end do
   print *, 'PASS fortran-string-to-real'
end program main
