! Independent MIT consumer; see licenses/fstats-summaries-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use fstats_binomial_distribution,only: &
      binomial_distribution
   implicit none
   type(binomial_distribution)::law
   real(wp),parameter::a(*)=[ &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      5.0_wp, 5.0_wp, 5.0_wp, &
      5.0_wp, 5.0_wp, 5.0_wp, &
      5.0_wp, 5.0_wp, 5.0_wp, &
      5.0_wp, 5.0_wp, 5.0_wp, &
      5.0_wp, 5.0_wp, 5.0_wp, &
      5.0_wp, 5.0_wp, 5.0_wp, &
      5.0_wp, 5.0_wp, 5.0_wp, &
      5.0_wp, 5.0_wp, 5.0_wp, &
      5.0_wp, 5.0_wp, 5.0_wp, &
      5.0_wp, 5.0_wp, 5.0_wp, &
      5.0_wp, 5.0_wp, 5.0_wp, &
      5.0_wp, 5.0_wp, 5.0_wp, &
      5.0_wp, 5.0_wp, 5.0_wp, &
      5.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp]
   real(wp),parameter::b(*)=[ &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.125_wp, 0.125_wp, 0.125_wp, &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.875_wp, 0.875_wp, 0.875_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.125_wp, 0.125_wp, &
      0.125_wp, 0.125_wp, 0.5_wp, &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.875_wp, 0.875_wp, 0.875_wp, &
      0.875_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.125_wp, 0.125_wp, &
      0.125_wp, 0.125_wp, 0.125_wp, &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 0.5_wp, 0.875_wp, &
      0.875_wp, 0.875_wp, 0.875_wp, &
      0.875_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.125_wp, &
      0.125_wp, 0.125_wp, 0.125_wp, &
      0.125_wp, 0.125_wp, 0.125_wp, &
      0.125_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.875_wp, 0.875_wp, 0.875_wp, &
      0.875_wp, 0.875_wp, 0.875_wp, &
      0.875_wp, 0.875_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.125_wp, &
      0.125_wp, 0.125_wp, 0.125_wp, &
      0.125_wp, 0.125_wp, 0.125_wp, &
      0.125_wp, 0.125_wp, 0.125_wp, &
      0.125_wp, 0.125_wp, 0.125_wp, &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 0.875_wp, 0.875_wp, &
      0.875_wp, 0.875_wp, 0.875_wp, &
      0.875_wp, 0.875_wp, 0.875_wp, &
      0.875_wp, 0.875_wp, 0.875_wp, &
      0.875_wp, 0.875_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp]
   real(wp),parameter::x(*)=[ &
      -1.0_wp, 0.0_wp, 1.0_wp, &
      -1.0_wp, 0.0_wp, 1.0_wp, &
      -1.0_wp, 0.0_wp, 1.0_wp, &
      -1.0_wp, 0.0_wp, 1.0_wp, &
      -1.0_wp, 0.0_wp, 1.0_wp, &
      -1.0_wp, 0.0_wp, 1.0_wp, &
      2.0_wp, -1.0_wp, 0.0_wp, &
      1.0_wp, 2.0_wp, -1.0_wp, &
      0.0_wp, 1.0_wp, 2.0_wp, &
      -1.0_wp, 0.0_wp, 1.0_wp, &
      2.0_wp, -1.0_wp, 0.0_wp, &
      1.0_wp, 2.0_wp, -1.0_wp, &
      0.0_wp, 1.0_wp, 2.0_wp, &
      3.0_wp, -1.0_wp, 0.0_wp, &
      1.0_wp, 2.0_wp, 3.0_wp, &
      -1.0_wp, 0.0_wp, 1.0_wp, &
      2.0_wp, 3.0_wp, -1.0_wp, &
      0.0_wp, 1.0_wp, 2.0_wp, &
      3.0_wp, -1.0_wp, 0.0_wp, &
      1.0_wp, 2.0_wp, 3.0_wp, &
      -1.0_wp, 0.0_wp, 1.0_wp, &
      2.0_wp, 3.0_wp, 4.0_wp, &
      5.0_wp, 6.0_wp, -1.0_wp, &
      0.0_wp, 1.0_wp, 2.0_wp, &
      3.0_wp, 4.0_wp, 5.0_wp, &
      6.0_wp, -1.0_wp, 0.0_wp, &
      1.0_wp, 2.0_wp, 3.0_wp, &
      4.0_wp, 5.0_wp, 6.0_wp, &
      -1.0_wp, 0.0_wp, 1.0_wp, &
      2.0_wp, 3.0_wp, 4.0_wp, &
      5.0_wp, 6.0_wp, -1.0_wp, &
      0.0_wp, 1.0_wp, 2.0_wp, &
      3.0_wp, 4.0_wp, 5.0_wp, &
      6.0_wp, -1.0_wp, 0.0_wp, &
      1.0_wp, 2.0_wp, 3.0_wp, &
      4.0_wp, 5.0_wp, 6.0_wp, &
      7.0_wp, 8.0_wp, 9.0_wp, &
      10.0_wp, 11.0_wp, -1.0_wp, &
      0.0_wp, 1.0_wp, 2.0_wp, &
      3.0_wp, 4.0_wp, 5.0_wp, &
      6.0_wp, 7.0_wp, 8.0_wp, &
      9.0_wp, 10.0_wp, 11.0_wp, &
      -1.0_wp, 0.0_wp, 1.0_wp, &
      2.0_wp, 3.0_wp, 4.0_wp, &
      5.0_wp, 6.0_wp, 7.0_wp, &
      8.0_wp, 9.0_wp, 10.0_wp, &
      11.0_wp, -1.0_wp, 0.0_wp, &
      1.0_wp, 2.0_wp, 3.0_wp, &
      4.0_wp, 5.0_wp, 6.0_wp, &
      7.0_wp, 8.0_wp, 9.0_wp, &
      10.0_wp, 11.0_wp, -1.0_wp, &
      0.0_wp, 1.0_wp, 2.0_wp, &
      3.0_wp, 4.0_wp, 5.0_wp, &
      6.0_wp, 7.0_wp, 8.0_wp, &
      9.0_wp, 10.0_wp, 11.0_wp]
   real(wp),parameter::pdf(*)=[ &
      0.0_wp, 1.0_wp, 0.0_wp, &
      0.0_wp, 1.0_wp, 0.0_wp, &
      0.0_wp, 1.0_wp, 0.0_wp, &
      0.0_wp, 1.0_wp, 0.0_wp, &
      0.0_wp, 1.0_wp, 0.0_wp, &
      0.0_wp, 1.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.875_wp, &
      0.125_wp, 0.0_wp, 0.0_wp, &
      0.5_wp, 0.5_wp, 0.0_wp, &
      0.0_wp, 0.125_wp, 0.875_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      1.0_wp, 0.0_wp, 0.0_wp, &
      1.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.765625_wp, &
      0.21875_wp, 0.015625_wp, 0.0_wp, &
      0.0_wp, 0.25_wp, 0.5_wp, &
      0.25_wp, 0.0_wp, 0.0_wp, &
      0.015625_wp, 0.21875_wp, 0.765625_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 1.0_wp, 0.0_wp, &
      0.0_wp, 1.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.512908935546875_wp, 0.366363525390625_wp, 0.10467529296875_wp, &
      0.01495361328125_wp, 0.001068115234375_wp, 0.000030517578125_wp, &
      0.0_wp, 0.0_wp, 0.03125_wp, &
      0.15625_wp, 0.3125_wp, 0.3125_wp, &
      0.15625_wp, 0.03125_wp, 0.0_wp, &
      0.0_wp, 0.000030517578125_wp, 0.001068115234375_wp, &
      0.01495361328125_wp, 0.10467529296875_wp, 0.366363525390625_wp, &
      0.512908935546875_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 1.0_wp, &
      0.0_wp, 0.0_wp, 1.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.263075576163828373_wp, 0.375822251662611961_wp, 0.241600018925964832_wp, &
      0.0920381024479866028_wp, 0.0230095256119966507_wp, 0.00394449010491371155_wp, &
      0.000469582155346870422_wp, 0.0000383332371711730957_wp, 2.05356627702713013e-6_wp, &
      6.51925802230834961e-8_wp, 9.31322574615478516e-10_wp, 0.0_wp, &
      0.0_wp, 0.0009765625_wp, 0.009765625_wp, &
      0.0439453125_wp, 0.1171875_wp, 0.205078125_wp, &
      0.24609375_wp, 0.205078125_wp, 0.1171875_wp, &
      0.0439453125_wp, 0.009765625_wp, 0.0009765625_wp, &
      0.0_wp, 0.0_wp, 9.31322574615478516e-10_wp, &
      6.51925802230834961e-8_wp, 2.05356627702713013e-6_wp, 0.0000383332371711730957_wp, &
      0.000469582155346870422_wp, 0.00394449010491371155_wp, 0.0230095256119966507_wp, &
      0.0920381024479866028_wp, 0.241600018925964832_wp, 0.375822251662611961_wp, &
      0.263075576163828373_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 1.0_wp, 0.0_wp]
   real(wp),parameter::cdf(*)=[ &
      0.0_wp, 1.0_wp, 1.0_wp, &
      0.0_wp, 1.0_wp, 1.0_wp, &
      0.0_wp, 1.0_wp, 1.0_wp, &
      0.0_wp, 1.0_wp, 1.0_wp, &
      0.0_wp, 1.0_wp, 1.0_wp, &
      0.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 0.0_wp, 0.875_wp, &
      1.0_wp, 1.0_wp, 0.0_wp, &
      0.5_wp, 1.0_wp, 1.0_wp, &
      0.0_wp, 0.125_wp, 1.0_wp, &
      1.0_wp, 0.0_wp, 0.0_wp, &
      1.0_wp, 1.0_wp, 0.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 0.0_wp, 0.765625_wp, &
      0.984375_wp, 1.0_wp, 1.0_wp, &
      0.0_wp, 0.25_wp, 0.75_wp, &
      1.0_wp, 1.0_wp, 0.0_wp, &
      0.015625_wp, 0.234375_wp, 1.0_wp, &
      1.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 1.0_wp, 1.0_wp, &
      0.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 0.0_wp, &
      0.512908935546875_wp, 0.8792724609375_wp, 0.98394775390625_wp, &
      0.9989013671875_wp, 0.999969482421875_wp, 1.0_wp, &
      1.0_wp, 0.0_wp, 0.03125_wp, &
      0.1875_wp, 0.5_wp, 0.8125_wp, &
      0.96875_wp, 1.0_wp, 1.0_wp, &
      0.0_wp, 0.000030517578125_wp, 0.0010986328125_wp, &
      0.01605224609375_wp, 0.1207275390625_wp, 0.487091064453125_wp, &
      1.0_wp, 1.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 1.0_wp, &
      1.0_wp, 0.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 0.0_wp, &
      0.263075576163828373_wp, 0.638897827826440334_wp, 0.880497846752405167_wp, &
      0.972535949200391769_wp, 0.99554547481238842_wp, 0.999489964917302132_wp, &
      0.999959547072649002_wp, 0.999997880309820175_wp, 0.999999933876097202_wp, &
      0.999999999068677425_wp, 1.0_wp, 1.0_wp, &
      0.0_wp, 0.0009765625_wp, 0.0107421875_wp, &
      0.0546875_wp, 0.171875_wp, 0.376953125_wp, &
      0.623046875_wp, 0.828125_wp, 0.9453125_wp, &
      0.9892578125_wp, 0.9990234375_wp, 1.0_wp, &
      1.0_wp, 0.0_wp, 9.31322574615478516e-10_wp, &
      6.61239027976989746e-8_wp, 2.1196901798248291e-6_wp, 0.0000404529273509979248_wp, &
      0.000510035082697868347_wp, 0.0044545251876115799_wp, 0.0274640507996082306_wp, &
      0.119502153247594833_wp, 0.361102172173559666_wp, 0.736924423836171627_wp, &
      1.0_wp, 1.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 1.0_wp, 1.0_wp]
   real(wp),parameter::survival(*)=[ &
      1.0_wp, 0.0_wp, 0.0_wp, &
      1.0_wp, 0.0_wp, 0.0_wp, &
      1.0_wp, 0.0_wp, 0.0_wp, &
      1.0_wp, 0.0_wp, 0.0_wp, &
      1.0_wp, 0.0_wp, 0.0_wp, &
      1.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 1.0_wp, 0.125_wp, &
      0.0_wp, 0.0_wp, 1.0_wp, &
      0.5_wp, 0.0_wp, 0.0_wp, &
      1.0_wp, 0.875_wp, 0.0_wp, &
      0.0_wp, 1.0_wp, 1.0_wp, &
      0.0_wp, 0.0_wp, 1.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 1.0_wp, 0.234375_wp, &
      0.015625_wp, 0.0_wp, 0.0_wp, &
      1.0_wp, 0.75_wp, 0.25_wp, &
      0.0_wp, 0.0_wp, 1.0_wp, &
      0.984375_wp, 0.765625_wp, 0.0_wp, &
      0.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 0.0_wp, 0.0_wp, &
      1.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 1.0_wp, &
      0.487091064453125_wp, 0.1207275390625_wp, 0.01605224609375_wp, &
      0.0010986328125_wp, 0.000030517578125_wp, 0.0_wp, &
      0.0_wp, 1.0_wp, 0.96875_wp, &
      0.8125_wp, 0.5_wp, 0.1875_wp, &
      0.03125_wp, 0.0_wp, 0.0_wp, &
      1.0_wp, 0.999969482421875_wp, 0.9989013671875_wp, &
      0.98394775390625_wp, 0.8792724609375_wp, 0.512908935546875_wp, &
      0.0_wp, 0.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 0.0_wp, &
      0.0_wp, 1.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 1.0_wp, &
      0.736924423836171627_wp, 0.361102172173559666_wp, 0.119502153247594833_wp, &
      0.0274640507996082306_wp, 0.0044545251876115799_wp, 0.000510035082697868347_wp, &
      0.0000404529273509979248_wp, 2.1196901798248291e-6_wp, 6.61239027976989746e-8_wp, &
      9.31322574615478516e-10_wp, 0.0_wp, 0.0_wp, &
      1.0_wp, 0.9990234375_wp, 0.9892578125_wp, &
      0.9453125_wp, 0.828125_wp, 0.623046875_wp, &
      0.376953125_wp, 0.171875_wp, 0.0546875_wp, &
      0.0107421875_wp, 0.0009765625_wp, 0.0_wp, &
      0.0_wp, 1.0_wp, 0.999999999068677425_wp, &
      0.999999933876097202_wp, 0.999997880309820175_wp, 0.999959547072649002_wp, &
      0.999489964917302132_wp, 0.99554547481238842_wp, 0.972535949200391769_wp, &
      0.880497846752405167_wp, 0.638897827826440334_wp, 0.263075576163828373_wp, &
      0.0_wp, 0.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 0.0_wp, 0.0_wp]
   integer::i

   do i=1,size(x)
      law%n=nint(a(i));law%p=b(i)
      call probability_check(law%pdf(x(i)),pdf(i))
      call probability_check(law%cdf(x(i)),cdf(i))
      call probability_check(law%survival(x(i)),survival(i))
      if(pdf(i)>0) call check(law%log_pdf(x(i)),log(pdf(i)))
   end do
   print '(a,i0)', 'Independent distribution reference cases: ',size(x)

   print '(a)', 'PASS fstats-binomial-boundaries-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in)::actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-10_wp*max(1._wp,abs(expected))) then
         print *, 'Actual, expected:',actual,expected
         error stop 'Independent reference'
      end if
   end subroutine
   subroutine probability_check(actual,expected)
      real(wp),intent(in)::actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite probability'
      if(abs(actual-expected)>2.e-9_wp*max(1.e-30_wp,abs(expected))) then
         print *, 'Actual probability, expected:',actual,expected
         error stop 'Independent probability reference'
      end if
   end subroutine
   subroutine insertion_sort(x)
      real(wp),intent(inout)::x(:)
      real(wp)::value
      integer::i,j
      do i=2,size(x)
         value=x(i);j=i-1
         do while(j>=1)
            if(x(j)<=value) exit
            x(j+1)=x(j);j=j-1
         end do
         x(j+1)=value
      end do
   end subroutine
   function local_median(sorted) result(value)
      real(wp),intent(in)::sorted(:)
      real(wp)::value
      integer::n
      n=size(sorted);value=(sorted((n+1)/2)+sorted(n/2+1))/2
   end function
end program
