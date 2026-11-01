! Independent MIT consumer; see licenses/distribution-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_stats_distribution_normal, only: pdf_normal
   implicit none
   real(real64),parameter :: reference(65)=[ &
      5.0522710835368922879501846e-15_real64, &
      3.6182944511125171989821818e-14_real64, &
      2.4343205330290098258746144e-13_real64, &
      1.5385379505612750262573696e-12_real64, &
      9.1347204083645933428686139e-12_real64, &
      5.0949379588436833246326552e-11_real64, &
      2.6695566147628519167024309e-10_real64, &
      1.3140018181558838857664874e-9_real64, &
      6.0758828498232854869963077e-9_real64, &
      2.6392432035705733310052792e-8_real64, &
      0.00000010769760042543276358782031_real64, &
      0.00000041284709886299983675102061_real64, &
      0.0000014867195147342977079082396_real64, &
      0.0000050295072885924453467347469_real64, &
      0.000015983741106905474434413971_real64, &
      0.000047718636541204945439742643_real64, &
      0.00013383022576488535177407449_real64, &
      0.00035259568236744539030948623_real64, &
      0.00087268269504576006560119296_real64, &
      0.002029048057299767785656041_real64, &
      0.0044318484119380071756023527_real64, &
      0.0090935625015910527700548728_real64, &
      0.017528300493568537362158322_real64, &
      0.031739651835667415749840308_real64, &
      0.0539909665131880519505642_real64, &
      0.086277318826511514431669433_real64, &
      0.12951759566589172761409956_real64, &
      0.18264908538902190499104456_real64, &
      0.24197072451914334979783019_real64, &
      0.30113743215480440493167121_real64, &
      0.35206532676429947777468044_real64, &
      0.38666811680284920694122575_real64, &
      0.39894228040143267793994606_real64, &
      0.38666811680284920694122575_real64, &
      0.35206532676429947777468044_real64, &
      0.30113743215480440493167121_real64, &
      0.24197072451914334979783019_real64, &
      0.18264908538902190499104456_real64, &
      0.12951759566589172761409956_real64, &
      0.086277318826511514431669433_real64, &
      0.0539909665131880519505642_real64, &
      0.031739651835667415749840308_real64, &
      0.017528300493568537362158322_real64, &
      0.0090935625015910527700548728_real64, &
      0.0044318484119380071756023527_real64, &
      0.002029048057299767785656041_real64, &
      0.00087268269504576006560119296_real64, &
      0.00035259568236744539030948623_real64, &
      0.00013383022576488535177407449_real64, &
      0.000047718636541204945439742643_real64, &
      0.000015983741106905474434413971_real64, &
      0.0000050295072885924453467347469_real64, &
      0.0000014867195147342977079082396_real64, &
      0.00000041284709886299983675102061_real64, &
      0.00000010769760042543276358782031_real64, &
      2.6392432035705733310052792e-8_real64, &
      6.0758828498232854869963077e-9_real64, &
      1.3140018181558838857664874e-9_real64, &
      2.6695566147628519167024309e-10_real64, &
      5.0949379588436833246326552e-11_real64, &
      9.1347204083645933428686139e-12_real64, &
      1.5385379505612750262573696e-12_real64, &
      2.4343205330290098258746144e-13_real64, &
      3.6182944511125171989821818e-14_real64, &
      5.0522710835368922879501846e-15_real64 ]
   real(real64),parameter :: locations(3)=[-1.5_real64,0._real64,2.25_real64]
   real(real64),parameter :: scales(3)=[0.25_real64,1._real64,4._real64]
   real(real64) :: x,z,expected,actual,previous
   integer :: a,b,i,checks
   checks=0
   do a=1,3
      do b=1,3
         previous=0
         do i=1,65
            z=real(i-33,real64)/4
            x=locations(a)+scales(b)*z
            expected=reference(i)/scales(b)
            actual=pdf_normal(x,locations(a),scales(b))
            call verify(actual,expected)
            checks=checks+1
         end do
      end do
   end do
   print '(a,i0)', 'Normal references from independent 80/120-digit constants, z=-8..8, nine location/scale pairs: ',checks
   print '(a)', 'PASS stdlib-normal-pdf-reference'
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
