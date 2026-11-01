! Independent MIT-licensed driver; see licenses/random-references-drivers-MIT.txt.
program reference_random_spacing
   use pointsets, only: random_spacing
   use select_precision, only: wp
   use, intrinsic :: iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: sizes(*)=[0,1,2,3,9,33,129],seeds(*)=[42,1729,314159],draws=20000
   integer :: nseed,sd,interval,sz,n,i,j,runs,entries,noops,cdf_cases,lower_count,upper_count
   integer, allocatable :: seed(:)
   real(wp), allocatable :: x(:),raw(:),replay(:)
   real(wp) :: left,right,next_actual,next_expected,sample(3)
   real(real64) :: expected,den,error,max_error,limit,p_lower,p_upper,cdf_error,max_cdf,average
   call random_seed(size=nseed)
   allocate(seed(nseed))
   runs=0; entries=0; noops=0; cdf_cases=0; max_error=0; max_cdf=0
   do sd=1,size(seeds)
      seed=[(seeds(sd)+37*i,i=1,nseed)]
      do interval=1,3
         left=0; right=1
         if (interval==2) then
            left=-3.5_wp; right=2.25_wp
         else if (interval==3) then
            left=0.25_wp; right=left
         end if
         do sz=1,size(sizes)
            n=sizes(sz)
            allocate(x(n),raw(n),replay(n)); x=-99
            call random_seed(put=seed)
            call random_spacing(x,left,right)
            call random_number(next_actual)
            call random_seed(put=seed)
            if (n>1) call random_number(raw)
            call random_number(next_expected)
            if (next_actual/=next_expected) error stop 'unexpected random-state consumption'
            if (n<=1) then
               if (any(x/=-99)) error stop 'empty/singleton input should remain unchanged'
               noops=noops+1
            else
               if (.not.all(ieee_is_finite(x))) error stop 'nonfinite random coordinates'
               if (any(x(2:)<x(:n-1))) error stop 'coordinates not nondecreasing'
               limit=8*real(n,real64)*real(epsilon(left),real64)
               den=sum(real(raw(2:),real64))
               if (den<=0) error stop 'fixture has zero increment sum'
               do i=1,n
                  expected=real(left,real64)+real(right-left,real64)*sum(real(raw(2:i),real64))/den
                  error=abs(real(x(i),real64)-expected)/(1+max(abs(real(left,real64)),abs(real(right,real64))))
                  if (error>limit) error stop 'independent normalized-increment reference differs'
                  max_error=max(max_error,error); entries=entries+1
               end do
               if (abs(x(1)-left)>limit .or. abs(x(n)-right)>limit) error stop 'interval endpoint differs'
            end if
            call random_seed(put=seed)
            replay=-99
            call random_spacing(replay,left,right)
            if (any(replay/=x)) error stop 'seeded replay differs'
            runs=runs+1
            deallocate(x,raw,replay)
         end do
      end do
      ! With three points, the interior coordinate is U/(U+V), not uniform.
      call random_seed(put=seed)
      lower_count=0; upper_count=0; average=0
      do j=1,draws
         call random_spacing(sample,0.0_wp,1.0_wp)
         if (.not.all(ieee_is_finite(sample))) error stop 'nonfinite CDF sample'
         if (sample(2)<0 .or. sample(2)>1) error stop 'CDF sample outside interval'
         if (sample(2)<=0.25_wp) lower_count=lower_count+1
         if (sample(2)<=0.75_wp) upper_count=upper_count+1
         average=average+real(sample(2),real64)
      end do
      p_lower=real(lower_count,real64)/draws; p_upper=real(upper_count,real64)/draws
      cdf_error=max(abs(p_lower-1.0_real64/6),abs(p_upper-5.0_real64/6))
      if (cdf_error>0.015_real64 .or. abs(average/draws-0.5_real64)>0.015_real64) &
         error stop 'normalized-uniform-increment law smoke check failed'
      if (abs(p_lower-0.25_real64)<0.04_real64) error stop 'fixture fails to distinguish uniform interior point'
      max_cdf=max(max_cdf,cdf_error); cdf_cases=cdf_cases+1
      print '(a,i8,a,3f12.7)', 'Seed ',seeds(sd),'; empirical CDF at 1/4,3/4 and mean: ', &
         p_lower,p_upper,average/draws
   end do
   print '(a,i0,a,i0,a,i0)', 'Spacing fixtures: ',runs,'; reference coordinates: ',entries,'; no-op fixtures: ',noops
   print '(a,i0,a,i0)', 'Three-point law samples: ',cdf_cases*draws,'; seed groups: ',cdf_cases
   print '(a,2es14.5)', 'Max normalized coordinate and CDF errors: ',max_error,max_cdf
   print '(a)', 'Normalized uniform increments are not uniform order statistics; no randomness certification.'
   print '(a)', 'PASS pointsets-random-reference'
end program
