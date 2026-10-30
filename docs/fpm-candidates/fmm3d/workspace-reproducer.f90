program main
 use, intrinsic :: iso_fortran_env, only: real64, int64
 use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
 implicit none
 real(real64) :: workspace(251)
 workspace = huge(1.0_real64)
 call l3dtaevalhessdini(3_int64,workspace)
 if (abs(workspace(1)-1.0_real64)>1.0e-12_real64) error stop 'Incorrect first coefficient'
 if (count(abs(workspace)<huge(1.0_real64))<5) error stop 'Coefficients missing'
 if (.not.all(ieee_is_finite(workspace))) error stop 'Nonfinite coefficient'
 if (workspace(251)/=huge(1.0_real64)) error stop 'Workspace sentinel overwritten'
 print *, 'PASS checked workspace initialization'
end program main
