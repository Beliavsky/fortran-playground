! Independent MIT consumer; see licenses/integrals-tensors-ten-drivers-MIT.txt.
module integrand_data
   use iso_fortran_env, only: wp=>real64
   implicit none
   real(wp) :: rate,center,exponent
   integer :: power
contains
   function f(x) result(y)
      real(wp),intent(in) :: x
      real(wp) :: y
      y=x**power
   end function
end module
program main
   use integrand_data
   use quadpack, only: dqaws
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp),parameter :: expected_values(*)=[ &
      3.14159265358979324_wp, -4.35517218060720426_wp, -4.35517218060720426_wp, &
      0.869837855632015082_wp, 1.57079632679489662_wp, -0.606789763508705511_wp, &
      -3.74838241709849875_wp, 0.434918927816007541_wp, 1.17809724509617246_wp, &
      -0.258742781782167056_wp, -3.40033543537196029_wp, 0.281537095889819956_wp, &
      0.981747704246810387_wp, -0.150169137868685188_wp, -3.16086209755890371_wp, &
      0.204846179926726164_wp, 2.0_wp, -4.0_wp, &
      -1.22741127776021876_wp, 0.585218154431078906_wp, 0.666666666666666667_wp, &
      -0.444444444444444444_wp, -0.853581537031184032_wp, 0.242149187287299445_wp, &
      0.4_wp, -0.16_wp, -0.672148922218710419_wp, &
      0.136716466447390222_wp, 0.285714285714285714_wp, -0.0816326530612244898_wp, &
      -0.561739026074589075_wp, 0.0894325494387367713_wp, 1.57079632679489662_wp, &
      -3.74838241709849875_wp, -0.606789763508705511_wp, 0.434918927816007541_wp, &
      0.392699081698724155_wp, -0.348046981726538455_wp, -0.348046981726538455_wp, &
      0.153381831926187585_wp, 0.196349540849362077_wp, -0.108573643913481868_wp, &
      -0.239473337813056587_wp, 0.0766909159630937924_wp, 0.122718463030851298_wp, &
      -0.049450757991298473_wp, -0.180350451890873191_wp, 0.0455137904942123896_wp, &
      2.0_wp, -1.22741127776021876_wp, -4.0_wp, &
      0.585218154431078906_wp, 1.33333333333333333_wp, -0.37382974072903473_wp, &
      -3.55555555555555556_wp, 0.343068967143779461_wp, 1.06666666666666667_wp, &
      -0.192397125916561118_wp, -3.27111111111111111_wp, 0.237636246303870238_wp, &
      0.914285714285714286_wp, -0.121374407248208849_wp, -3.06503401360544218_wp, &
      0.179487442472614466_wp, 1.0_wp, -1.0_wp, &
      -1.0_wp, 0.355065933151773564_wp, 0.5_wp, &
      -0.25_wp, -0.75_wp, 0.177532966575886782_wp, &
      0.333333333333333333_wp, -0.111111111111111111_wp, -0.611111111111111111_wp, &
      0.109096051791331929_wp, 0.25_wp, -0.0625_wp, &
      -0.520833333333333333_wp, 0.074877594399054502_wp, 0.666666666666666667_wp, &
      -0.853581537031184032_wp, -0.444444444444444444_wp, 0.242149187287299445_wp, &
      0.266666666666666667_wp, -0.181432614812473613_wp, -0.284444444444444444_wp, &
      0.105432720839909223_wp, 0.152380952380952381_wp, -0.0710227186683522685_wp, &
      -0.206077097505668934_wp, 0.0581488038312557726_wp, 0.101587301587301587_wp, &
      -0.0360610011580902249_wp, -0.159959687578735198_wp, 0.0365311117166497347_wp, &
      1.57079632679489662_wp, -0.606789763508705511_wp, -3.74838241709849875_wp, &
      0.434918927816007541_wp, 1.17809724509617246_wp, -0.258742781782167056_wp, &
      -3.40033543537196029_wp, 0.281537095889819956_wp, 0.981747704246810387_wp, &
      -0.150169137868685188_wp, -3.16086209755890371_wp, 0.204846179926726164_wp, &
      0.859029241215959089_wp, -0.100718379877386715_wp, -2.98051164566803052_wp, &
      0.159332389432513774_wp, 0.666666666666666667_wp, -0.444444444444444444_wp, &
      -0.853581537031184032_wp, 0.242149187287299445_wp, 0.4_wp, &
      -0.16_wp, -0.672148922218710419_wp, 0.136716466447390222_wp, &
      0.285714285714285714_wp, -0.0816326530612244898_wp, -0.561739026074589075_wp, &
      0.0894325494387367713_wp, 0.222222222222222222_wp, -0.049382716049382716_wp, &
      -0.486290847440729774_wp, 0.0637663245446893589_wp, 0.392699081698724155_wp, &
      -0.348046981726538455_wp, -0.348046981726538455_wp, 0.153381831926187585_wp, &
      0.196349540849362077_wp, -0.108573643913481868_wp, -0.239473337813056587_wp, &
      0.0766909159630937924_wp, 0.122718463030851298_wp, -0.049450757991298473_wp, &
      -0.180350451890873191_wp, 0.0455137904942123896_wp, 0.0859029241215959089_wp, &
      -0.0272524228120578532_wp, -0.143425901147930416_wp, 0.0299252277597716883_wp]
   integer,parameter :: limit=300,lenw=4*limit
   real(wp) :: result,abserr,work(lenw),expected,a,b
   integer :: ier,neval,last,iwork(limit),i,j,k,cases

   real(wp) :: alpha,beta
   integer :: integr,index
   cases=0; index=0; a=0; b=1
   do i=-1,1
      alpha=real(i,wp)/2
      do j=-1,1
         beta=real(j,wp)/2
         do power=0,3
            do integr=1,4
               index=index+1; expected=expected_values(index)
               call dqaws(f,a,b,alpha,beta,integr,1.e-10_wp,1.e-10_wp,result,abserr,neval, &
                  ier,limit,lenw,last,iwork,work)
               call status_check(); call check(result,expected); cases=cases+1
            end do
         end do
      end do
   end do
   if(index/=size(expected_values)) error stop 'Reference consumption'
   print '(a,i0)', 'Algebraic/logarithmic endpoint weights against beta derivatives: ',cases
   print '(a)', 'PASS quadpack-endpoint-weights-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-9_wp*max(1._wp,abs(expected))) error stop 'Independent reference'
   end subroutine
   subroutine status_check()
      if(ier/=0) error stop 'QUADPACK unsuccessful status'
      if(neval<=0.or.last<=0) error stop 'QUADPACK work counters'
      if(.not.ieee_is_finite(abserr).or.abserr<0) error stop 'Invalid error estimate'
   end subroutine
end program
