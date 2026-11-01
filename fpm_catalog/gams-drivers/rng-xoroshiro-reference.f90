! Independent MIT consumer; see licenses/helmholtz-streams-drivers-MIT.txt.
! Golden vectors: references/xoroshiro_vectors.py and xoroshiro-vectors.json.
program xoroshiro_reference
   use m_random, only: rng_t
   use, intrinsic :: iso_fortran_env, only: int64,real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer(int64), parameter :: prime=2147483647_int64,scale=4503599627370496_int64
   integer(int64), parameter :: seeds(2,15)=reshape([ &
      int(z'0000000000000001',int64),int(z'0000000000000002',int64), &
      int(z'0000000000000001',int64),int(z'0000000000000002',int64), &
      int(z'0000000000000001',int64),int(z'0000000000000002',int64), &
      int(z'FFFFFFFFFFFFFFFF',int64),int(z'0000000000000001',int64), &
      int(z'FFFFFFFFFFFFFFFF',int64),int(z'0000000000000001',int64), &
      int(z'FFFFFFFFFFFFFFFF',int64),int(z'0000000000000001',int64), &
      int(z'8000000000000000',int64),int(z'7FFFFFFFFFFFFFFF',int64), &
      int(z'8000000000000000',int64),int(z'7FFFFFFFFFFFFFFF',int64), &
      int(z'8000000000000000',int64),int(z'7FFFFFFFFFFFFFFF',int64), &
      int(z'00000000075BCD15',int64),int(z'000000003ADE68B1',int64), &
      int(z'00000000075BCD15',int64),int(z'000000003ADE68B1',int64), &
      int(z'00000000075BCD15',int64),int(z'000000003ADE68B1',int64), &
      int(z'0123456789ABCDEF',int64),int(z'FEDCBA9876543210',int64), &
      int(z'0123456789ABCDEF',int64),int(z'FEDCBA9876543210',int64), &
      int(z'0123456789ABCDEF',int64),int(z'FEDCBA9876543210',int64) &
      ],[2,15])
   integer(int64), parameter :: prefix(8,15)=reshape([ &
      int(z'0000000000000003',int64),int(z'0000006001030003',int64), &
      int(z'20C102C302000C03',int64),int(z'810180670D23AD61',int64), &
      int(z'26D13A4941333A42',int64),int(z'538A501C02F58B2E',int64), &
      int(z'2AB2076DEE382F7E',int64),int(z'30DFCFB722FECD9C',int64), &
      int(z'EA081299D29AD927',int64),int(z'DDE2899549F899C8',int64), &
      int(z'E9FBDBE2A1BFDA9C',int64),int(z'2D3A2ECAC8B96CC2',int64), &
      int(z'A811D60D632FA176',int64),int(z'157B37AF0380DAB3',int64), &
      int(z'9E4FD349BA2B1D03',int64),int(z'CAC7882CD2F53F71',int64), &
      int(z'54467869EA575CE9',int64),int(z'F13E10AD0CF279CD',int64), &
      int(z'80B67F904F7FBD17',int64),int(z'CE746E26FC29C30F',int64), &
      int(z'C5ED5E1E92CE81FC',int64),int(z'6DEE81DC2372074E',int64), &
      int(z'576FFEBF69A608FF',int64),int(z'37C32F9BF84EEC8B',int64), &
      int(z'0000000000000000',int64),int(z'FFFFFFDFFFFE0000',int64), &
      int(z'001FFDE1FE000401',int64),int(z'A0008021F7FF183E',int64), &
      int(z'81B77EFF1FD113FF',int64),int(z'FDBDFFDDFD401895',int64), &
      int(z'ABFD5946AAC10759',int64),int(z'D4C82A6EB9380EAD',int64), &
      int(z'2EBB42265FF3F3CD',int64),int(z'62D1F7E5D345D214',int64), &
      int(z'852BE2FE5A40E677',int64),int(z'8B0E802242885237',int64), &
      int(z'96F05D29CCB37DAE',int64),int(z'66253F44CA9715CB',int64), &
      int(z'A57952ECAE4B08E7',int64),int(z'301389B3A5A3DBEE',int64), &
      int(z'7205078518A5DCF2',int64),int(z'A53811B9E11A1A1D',int64), &
      int(z'3267D010E4258CDC',int64),int(z'B1468FA13314C731',int64), &
      int(z'CF8E28D89AA68D57',int64),int(z'497E8E24D1A63B22',int64), &
      int(z'9C068A357B0AA9C9',int64),int(z'5FB20D3DD7BF50BC',int64), &
      int(z'FFFFFFFFFFFFFFFF',int64),int(z'000000000080FFFE',int64), &
      int(z'EFE0809F007EFFFF',int64),int(z'00A000DDFC900B9E',int64), &
      int(z'8D80E8A9841F571F',int64),int(z'6BAF87F0E34224CF',int64), &
      int(z'6F307DAEF1119B7E',int64),int(z'820D652D6361D9D4',int64), &
      int(z'1A4F8E3A82386E7E',int64),int(z'3D59493ABD70AD87',int64), &
      int(z'7C0EB08A37C6CD83',int64),int(z'66FEA811D4298E20',int64), &
      int(z'0536E2FCF4875C68',int64),int(z'9F1C3015AA369660',int64), &
      int(z'329897EF81D31D6D',int64),int(z'331C298564FAB490',int64), &
      int(z'42168400D0782FE0',int64),int(z'5489B5B19DE7A5E7',int64), &
      int(z'D6285D0884E00C48',int64),int(z'AE32EAD2210E7D61',int64), &
      int(z'04299F2B47871BE9',int64),int(z'E1C75C781013EB6C',int64), &
      int(z'BB7560224986887A',int64),int(z'30E35E64DB2BBFD4',int64), &
      int(z'00000000423A35C6',int64),int(z'B0BC1AC88D21A5AB',int64), &
      int(z'CF2B32C2A2FCFBD6',int64),int(z'67944CF27C5F54FD',int64), &
      int(z'2B2831CE8A235C5A',int64),int(z'762652EF1531D004',int64), &
      int(z'5568F141CE3DCB86',int64),int(z'1D05E25A58D1AAB9',int64), &
      int(z'810C02F9BC046232',int64),int(z'304AB2438B779F93',int64), &
      int(z'269F92F4D901FF75',int64),int(z'0EF7075DAC8F4C2A',int64), &
      int(z'8C844E3739E9D705',int64),int(z'5A5FBB4DE7813B24',int64), &
      int(z'F6F2FA3DBCAC28E6',int64),int(z'3DB6A1EE7743452F',int64), &
      int(z'9CC4853D1B5C6AC9',int64),int(z'D08121ED511978A4',int64), &
      int(z'5B7017E8A21A8B87',int64),int(z'296969664A700F05',int64), &
      int(z'7117384717940653',int64),int(z'753C0BB31918064F',int64), &
      int(z'A5CF1AC686AAAD05',int64),int(z'72ACBBEEC53815DF',int64), &
      int(z'FFFFFFFFFFFFFFFF',int64),int(z'6789ABCDEF01DCB9',int64), &
      int(z'216FADC398A73130',int64),int(z'060B0BA313A13C59',int64), &
      int(z'4920437D8300EA80',int64),int(z'2FB0D5BA5CAFCC5A',int64), &
      int(z'5FF3CA78BCAEC9D2',int64),int(z'C4F3590CD05817CC',int64), &
      int(z'D678A1932E214621',int64),int(z'8A4C1E47D53313EF',int64), &
      int(z'EE1D57CE8E19B545',int64),int(z'438F10E8AFC03A25',int64), &
      int(z'ED7BA73830C0047E',int64),int(z'ADA68B7A34213E05',int64), &
      int(z'2B60A67655CAAB33',int64),int(z'597382D9B5E10D6A',int64), &
      int(z'D3D6AD5F9296CD0C',int64),int(z'914A3BDF76326F6B',int64), &
      int(z'AC955520ABEFB944',int64),int(z'CFB53D80845B264F',int64), &
      int(z'5441999012808CE5',int64),int(z'9E8E1020EA032797',int64), &
      int(z'7E61DD5BF609677E',int64),int(z'13D409D66703B2A9',int64) &
      ],[8,15])
   integer(int64), parameter :: expected_integer(*)=[ &
      1941895846_int64,1313938562_int64,1542720481_int64, &
      192422793_int64,1378303015_int64,1174268788_int64, &
      468487869_int64,2014768876_int64,454642981_int64, &
      790614674_int64,1503636214_int64,416336232_int64, &
      1683816592_int64,2133358670_int64,529020594_int64 &
      ]
   integer(int64), parameter :: expected_uniform(*)=[ &
      125224916_int64,95949674_int64,2053003890_int64, &
      1622350968_int64,2078434163_int64,1280079309_int64, &
      300889514_int64,754427825_int64,1839058556_int64, &
      421909431_int64,41773830_int64,1735978279_int64, &
      1419921227_int64,363383729_int64,462154641_int64 &
      ]
   type(rng_t) :: integer_rng(15),uniform_rng(15),replay
   integer(int64) :: integer_hash(15),uniform_hash(15),word,top,residue,again
   real(real64) :: u
   integer :: stream,sample,jumps,j,replayed
   integer_hash=0; uniform_hash=0; replayed=0
   do stream=1,15
      jumps=modulo(stream-1,3)
      call initialize(integer_rng(stream),seeds(:,stream),jumps)
      call initialize(uniform_rng(stream),seeds(:,stream),jumps)
   end do
   ! Interleave independent states, comparing both public output paths at every step.
   do sample=1,4096
      do stream=1,15
         word=integer_rng(stream)%int_64()
         u=uniform_rng(stream)%unif_01()
         if (sample<=8) then
            if (word/=prefix(sample,stream)) error stop 'integer golden prefix differs'
         end if
         if (.not.ieee_is_finite(u)) error stop 'nonfinite uniform output'
         if (u<0 .or. u>=1) error stop 'uniform range differs'
         top=int(u*real(scale,real64),int64)
         if (top/=shiftr(word,12)) error stop '52-bit uniform conversion differs'
         ! 2**64 modulo prime is 4; interpret negative signed words as unsigned.
         residue=modulo(word,prime)
         if (word<0) residue=modulo(residue+4,prime)
         integer_hash(stream)=modulo(65599_int64*integer_hash(stream)+residue,prime)
         uniform_hash(stream)=modulo(65599_int64*uniform_hash(stream)+top,prime)
      end do
   end do
   if (any(integer_hash/=expected_integer)) error stop 'independent integer stream checksum differs'
   if (any(uniform_hash/=expected_uniform)) error stop 'independent uniform stream checksum differs'
   do stream=1,15
      jumps=modulo(stream-1,3)
      call initialize(replay,seeds(:,stream),jumps)
      do sample=1,8
         again=replay%int_64()
         if (again/=prefix(sample,stream)) error stop 'seeded integer restart differs'
         replayed=replayed+1
      end do
   end do
   print '(a)', '15 interleaved streams: five nonzero seeds, no jump/default jump/two explicit jumps.'
   print '(a)', '61440 integer and 61440 uniform draws; 120 exact prefixes; 30 independent rolling hashes.'
   print '(a,i0)', 'Exact seeded restart entries: ',replayed
   print '(a)', 'Jump references use a GF(2) matrix raised to 2**64, not the package jump polynomial.'
   print '(a)', 'Bitstream/API agreement only; statistical quality, thread scheduling and normal reseeding unverified.'
   print '(a)', 'PASS rng-xoroshiro-reference'
contains
   subroutine initialize(rng,seed,jumps)
      type(rng_t), intent(inout) :: rng
      integer(int64), intent(in) :: seed(2)
      integer, intent(in) :: jumps
      integer :: j
      if (jumps==1) then
         call rng%set_seed(seed)
      else
         call rng%set_seed(seed,do_jump=.false.)
         do j=1,jumps
            call rng%jump()
         end do
      end if
   end subroutine
end program
