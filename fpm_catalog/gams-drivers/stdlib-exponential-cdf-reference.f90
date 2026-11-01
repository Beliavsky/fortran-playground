! Independent MIT consumer; see licenses/distribution-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_stats_distribution_exponential, only: cdf_exp
   implicit none
   real(real64),parameter :: reference(65)=[ &
      0.0_real64, &
      0.0_real64, &
      0.0_real64, &
      0.0_real64, &
      0.0_real64, &
      0.11750309741540459713510786_real64, &
      0.22119921692859513175482973_real64, &
      0.31271072120902780145479766_real64, &
      0.39346934028736657639620047_real64, &
      0.46473857148100975804337749_real64, &
      0.52763344725898529286195345_real64, &
      0.58313798032149159741470282_real64, &
      0.63212055882855767840447623_real64, &
      0.67534753264165027020293186_real64, &
      0.71349520313980989967511457_real64, &
      0.7471604041952535221890125_real64, &
      0.77686983985157017106671953_real64, &
      0.80308832479580594993871078_real64, &
      0.82622605654955487331928274_real64, &
      0.84664503315507153670443552_real64, &
      0.86466471676338730810600051_real64, &
      0.88056703173328038200412305_real64, &
      0.89460077543813566321678231_real64, &
      0.90698551078933651330013543_real64, &
      0.91791500137610120483047133_real64, &
      0.92756024296574853726165615_real64, &
      0.93607213879329242729756997_real64, &
      0.94358386049622265169373961_real64, &
      0.95021293163213605702065758_real64, &
      0.95606306637659258267325232_real64, &
      0.96122579216827799011310016_real64, &
      0.96578188168833396530144494_real64, &
      0.96980261657768149926021371_real64, &
      0.97335090266364451391261799_real64, &
      0.97648225414399089176384881_real64, &
      0.9792456621263002577846461_real64, &
      0.98168436111126581970628198_real64, &
      0.98383650541183412489439695_real64, &
      0.98573576609100074472671305_real64, &
      0.98741185775756600173242663_real64, &
      0.98889100346175769350385687_real64, &
      0.99019634496417817168512076_real64, &
      0.9913483047968793658229285_real64, &
      0.99236490578114003836372652_real64, &
      0.99326205300091453290336395_real64, &
      0.99405378264352790561358309_real64, &
      0.99475248160081861572350647_real64, &
      0.99536908126646675390731257_real64, &
      0.9959132285615359330065353_real64, &
      0.99639343686398426944446131_real64, &
      0.99681721920349033293201358_real64, &
      0.99719120580547448737748435_real64, &
      0.99752124782333364157695483_real64, &
      0.99781250888181711487672054_real64, &
      0.99806954586377229075778649_real64, &
      0.99829638020419742601370957_real64, &
      0.9984965608070224275526171_real64, &
      0.99867321956897300851900244_real64, &
      0.99882912037920882559904978_real64, &
      0.99896670236135236295859702_real64, &
      0.99908811803444548379199686_real64, &
      0.99919526698987538672930987_real64, &
      0.9992898256111574509364154_real64, &
      0.99937327330155154240265385_real64, &
      0.999446915629852166416898_real64 ]
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
            expected=reference(i)
            actual=cdf_exp(x,locations(a),scales(b))
            call verify(actual,expected)
            actual=cdf_exp(x-locations(a),1/scales(b))
            call verify(actual,expected)
            checks=checks+2
         end do
      end do
   end do
   print '(a,i0)', 'Exponential scale and rate overload references, shifted support and z=-0.5..7.5: ',checks
   print '(a)', 'PASS stdlib-exponential-cdf-reference'
contains
   subroutine verify(actual,expected)
      real(real64),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite distribution result'
      if(actual<0._real64) error stop 'Negative distribution result'
      if(abs(actual-expected)>3.e-14_real64*max(1._real64,abs(expected))) then
         print *, 'actual, expected: ',actual,expected
         error stop 'Independent distribution reference'
      end if
      if(actual>1._real64) error stop 'CDF exceeds one'
      if(actual+3.e-14_real64<previous) error stop 'Nonmonotone CDF'
      previous=actual
   end subroutine
end program
