program main
 use assert_m, only: assert
 implicit none
 call assert(.false., 'EXPECTED ASSERTION FAILURE: checks are enabled')
 print *, 'UNEXPECTED PASS'
end program main
