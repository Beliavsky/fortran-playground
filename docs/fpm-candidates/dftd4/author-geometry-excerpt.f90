! This file is part of mstore.
! SPDX-Identifier: Apache-2.0
!
! Licensed under the Apache License, Version 2.0 (the "License");
! you may not use this file except in compliance with the License.
! You may obtain a copy of the License at
!
!     http://www.apache.org/licenses/LICENSE-2.0
!
! Unless required by applicable law or agreed to in writing, software
! distributed under the License is distributed on an "AS IS" BASIS,
! WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
! See the License for the specific language governing permissions and
! limitations under the License.

! Geometry excerpt from mstore v0.4.0; complete source is linked in source-review.json.
subroutine mindless01(self)
   type(structure_type), intent(out) :: self
   integer, parameter :: nat = 16
   character(len=*), parameter :: sym(nat) = [character(len=4)::&
      & "Na", "H", "O", "H", "F", "H", "H", "O", "N", "H", "H", "Cl", "B", "B", "N", "Al"]
   real(wp), parameter :: xyz(3, nat) = reshape([&
      & -1.85528263484662_wp,  3.58670515364616_wp, -2.41763729306344_wp, &
      &  4.40178023537845_wp,  0.02338844412653_wp, -4.95457749372945_wp, &
      & -2.98706033463438_wp,  4.76252065456814_wp,  1.27043301573532_wp, &
      &  0.79980886075526_wp,  1.41103455609189_wp, -5.04655321620119_wp, &
      & -4.20647469409936_wp,  1.84275767548460_wp,  4.55038084858449_wp, &
      & -3.54356121843970_wp, -3.18835665176557_wp,  1.46240021785588_wp, &
      &  2.70032160109941_wp,  1.06818452504054_wp, -1.73234650374438_wp, &
      &  3.73114088824361_wp, -2.07001543363453_wp,  2.23160937604731_wp, &
      & -1.75306819230397_wp,  0.35951417150421_wp,  1.05323406177129_wp, &
      &  5.41755788583825_wp, -1.57881830078929_wp,  1.75394002750038_wp, &
      & -2.23462868255966_wp, -2.13856505054269_wp,  4.10922285746451_wp, &
      &  1.01565866207568_wp, -3.21952154552768_wp, -3.36050963020778_wp, &
      &  2.42119255723593_wp,  0.26626435093114_wp, -3.91862474360560_wp, &
      & -3.02526098819107_wp,  2.53667889095925_wp,  2.31664984740423_wp, &
      & -2.00438948664892_wp, -2.29235136977220_wp,  2.19782807357059_wp, &
      &  1.12226554109716_wp, -1.36942007032045_wp,  0.48455055461782_wp],&
      & shape(xyz))
   call new(self, sym, xyz)
end subroutine mindless01
