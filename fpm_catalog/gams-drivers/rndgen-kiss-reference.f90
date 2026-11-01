! Independent MIT-licensed driver; see licenses/random-references-drivers-MIT.txt.
program reference_kiss_streams
   use rndgen_mod, only: rndgen,rndSeed
   use, intrinsic :: iso_fortran_env, only: int32,int64,real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: streams=7,count=4096,continuation=257
   integer(int32), parameter :: seeds(streams)=[0,1,-1,12345,-67890,294727492,2147483646]
! BEGIN REFERENCE CONSTANTS
   integer(int64), parameter :: prefix(8,streams)=reshape([ &
      1761119782_int64, 1258461758_int64, 957194328_int64, 1842507483_int64, &
      1208524783_int64, 1652857723_int64, 2053757388_int64, 879438213_int64, &
      215227806_int64, 1405642535_int64, 1146595842_int64, 277176711_int64, &
      1818037016_int64, 2015763050_int64, 833496322_int64, 892211371_int64, &
      215227806_int64, 1405642535_int64, 1146595842_int64, 277176711_int64, &
      1818037016_int64, 2015763050_int64, 833496322_int64, 892211371_int64, &
      119035902_int64, 801032792_int64, 1351668714_int64, 1510475862_int64, &
      2107887406_int64, 1946816441_int64, 1708277923_int64, 1563380222_int64, &
      1390243629_int64, 736091383_int64, 159624430_int64, 1721960888_int64, &
      661694071_int64, 1548385597_int64, 1694887988_int64, 1408673621_int64, &
      1460433475_int64, 1552770090_int64, 1995302543_int64, 462454171_int64, &
      74143359_int64, 1453442776_int64, 1718954354_int64, 797438472_int64, &
      2126337207_int64, 1607088900_int64, 195281517_int64, 2146981700_int64, &
      1821595793_int64, 157919299_int64, 1601524667_int64, 1536048808_int64 &
      ],[8,streams])
   integer(int64), parameter :: expected_checksums(streams)=[ &
      34213082_int64, 1007654948_int64, 1007654948_int64, 1924117522_int64, &
      359022780_int64, 1855872359_int64, 1855580040_int64]
! END REFERENCE CONSTANTS
   type(rndgen) :: generators(streams)
   type(rndSeed) :: snapshot
   integer :: i,j
   integer(int32) :: seed
   integer(int64) :: checksum(streams),code
   real(real64) :: values(count,streams),tail(continuation),u
   checksum=0
   do j=1,streams
      seed=seeds(j)
      call generators(j)%init(seed)
   end do
   ! Interleave all objects, so shared-state contamination changes their exact vectors.
   do i=1,count
      do j=1,streams
         u=generators(j)%rnd()
         if (.not.ieee_is_finite(u) .or. u<0 .or. u>=1) error stop 'invalid uniform value'
         code=floor(u*2147483648.0_real64,kind=int64)
         if (u/=real(code,real64)/2147483648.0_real64) error stop 'value is not on the 31-bit grid'
         if (i<=8) then
            if (code/=prefix(i,j)) error stop 'independent integer prefix differs'
         end if
         checksum(j)=modulo(65599_int64*checksum(j)+code,2147483647_int64)
         values(i,j)=u
      end do
   end do
   if (any(checksum/=expected_checksums)) error stop 'independent whole-stream checksum differs'
   do j=1,streams
      call generators(j)%reset()
      do i=1,count
         if (generators(j)%rnd()/=values(i,j)) error stop 'reset replay differs'
      end do
      call generators(j)%save_seed(snapshot)
      do i=1,continuation
         tail(i)=generators(j)%rnd()
      end do
      call generators(j)%read_seed(snapshot)
      do i=1,continuation
         if (generators(j)%rnd()/=tail(i)) error stop 'in-memory state replay differs'
      end do
   end do
   print '(a,i0,a,i0)', 'Interleaved streams: ',streams,'; uniform outputs: ',streams*count
   print '(a,i0,a,i0)', 'Exact independent prefix entries: ',8*streams,'; whole-stream checksums: ',streams
   print '(a,i0,a,i0)', 'Exact reset replays: ',streams*count,'; saved-state continuations: ',streams*continuation
   print '(a)', 'GNU 16 wraparound convention checked; no statistical-quality or cross-compiler guarantee.'
   print '(a)', 'PASS rndgen-kiss-reference'
end program
