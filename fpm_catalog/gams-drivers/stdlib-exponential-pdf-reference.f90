! Independent MIT consumer; see licenses/distribution-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_stats_distribution_exponential, only: pdf_exp
   implicit none
   real(real64),parameter :: reference(65)=[ &
      0.0_real64, &
      0.0_real64, &
      0.0_real64, &
      0.0_real64, &
      1.0_real64, &
      0.88249690258459540286489214_real64, &
      0.77880078307140486824517027_real64, &
      0.68728927879097219854520234_real64, &
      0.60653065971263342360379953_real64, &
      0.53526142851899024195662251_real64, &
      0.47236655274101470713804655_real64, &
      0.41686201967850840258529718_real64, &
      0.36787944117144232159552377_real64, &
      0.32465246735834972979706814_real64, &
      0.28650479686019010032488543_real64, &
      0.2528395958047464778109875_real64, &
      0.22313016014842982893328047_real64, &
      0.19691167520419405006128922_real64, &
      0.17377394345044512668071726_real64, &
      0.15335496684492846329556448_real64, &
      0.13533528323661269189399949_real64, &
      0.11943296826671961799587695_real64, &
      0.10539922456186433678321769_real64, &
      0.093014489210663486699864573_real64, &
      0.082084998623898795169528674_real64, &
      0.072439757034251462738343853_real64, &
      0.063927861206707572702430026_real64, &
      0.056416139503777348306260389_real64, &
      0.049787068367863942979342416_real64, &
      0.043936933623407417326747682_real64, &
      0.038774207831722009886899835_real64, &
      0.034218118311666034698555059_real64, &
      0.030197383422318500739786292_real64, &
      0.026649097336355486087382011_real64, &
      0.023517745856009108236151185_real64, &
      0.020754337873699742215353898_real64, &
      0.018315638888734180293718021_real64, &
      0.016163494588165875105603047_real64, &
      0.014264233908999255273286946_real64, &
      0.012588142242433998267573368_real64, &
      0.011108996538242306496143134_real64, &
      0.0098036550358218283148792443_real64, &
      0.008651695203120634177071504_real64, &
      0.0076350942188599616362734837_real64, &
      0.0067379469990854670966360484_real64, &
      0.005946217356472094386416907_real64, &
      0.0052475183991813842764935293_real64, &
      0.0046309187335332460926874263_real64, &
      0.0040867714384640669934647027_real64, &
      0.0036065631360157305555386904_real64, &
      0.003182780796509667067986418_real64, &
      0.0028087941945255126225156484_real64, &
      0.0024787521766663584230451674_real64, &
      0.0021874911181828851232794638_real64, &
      0.001930454136227709242213512_real64, &
      0.001703619795802573986290427_real64, &
      0.0015034391929775724473829033_real64, &
      0.0013267804310269914809975625_real64, &
      0.0011708796207911744009502201_real64, &
      0.0010332976386476370414029838_real64, &
      0.00091188196555451620800313608_real64, &
      0.0008047330101246132706901273_real64, &
      0.00071017438884254906358460037_real64, &
      0.00062672669844845759734614938_real64, &
      0.00055308437014783358310200009_real64 ]
   real(real64),parameter :: locations(3)=[-1.5_real64,0._real64,2.25_real64]
   real(real64),parameter :: scales(3)=[0.25_real64,1._real64,4._real64]
   real(real64) :: x,z,expected,actual,previous
   integer :: a,b,i,checks
   checks=0
   do a=1,3
      do b=1,3
         previous=0
         do i=1,65
            z=real(i-5,real64)/8
            x=locations(a)+scales(b)*z
            expected=reference(i)/scales(b)
            actual=pdf_exp(x,locations(a),scales(b))
            call verify(actual,expected)
            actual=pdf_exp(x-locations(a),1/scales(b))
            call verify(actual,expected)
            checks=checks+2
         end do
      end do
   end do
   print '(a,i0)', 'Exponential scale and rate overload references, shifted support and z=-0.5..7.5: ',checks
   print '(a)', 'PASS stdlib-exponential-pdf-reference'
contains
   subroutine verify(actual,expected)
      real(real64),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite distribution result'
      if(actual<0._real64) error stop 'Negative distribution result'
      if(abs(actual-expected)>3.e-14_real64*max(1._real64,abs(expected))) then
         print *, 'actual, expected: ',actual,expected
         error stop 'Independent distribution reference'
      end if
   end subroutine
end program
