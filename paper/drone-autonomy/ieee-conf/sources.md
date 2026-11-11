# Sources

Every number in the paper, where it comes from. Regenerate with `make_all.py`.

## Value macros (generated/values.tex)

| Macro | Value | Meaning | Computed from |
|---|---|---|---|
| `\valResClassicalPre` | 21.4 | held-out RMSE before adapting, cm | results/summary.json -> tracking_residual / classical test_pre x100 |
| `\valResClassicalPost` | 21.4 | held-out RMSE after 3 stages, cm | results/summary.json -> tracking_residual / classical test_post x100 |
| `\valResClassicalCi` | 3.9 | 95% half-interval of held-out RMSE after adapting, cm | results/summary.json -> tracking_residual / classical test_post_ci x100 |
| `\valResClassicalOod` | 78.7 | OOD RMSE after 3 stages, cm | results/summary.json -> tracking_residual / classical ood_post x100 |
| `\valResClassicalOodCrash` | 34 | OOD crash rate after 3 stages, % | results/summary.json -> tracking_residual / classical ood_crash |
| `\valResLonePre` | 15.5 | held-out RMSE before adapting, cm | results/summary.json -> tracking_residual / l1 test_pre x100 |
| `\valResLonePost` | 15.5 | held-out RMSE after 3 stages, cm | results/summary.json -> tracking_residual / l1 test_post x100 |
| `\valResLoneCi` | 2.4 | 95% half-interval of held-out RMSE after adapting, cm | results/summary.json -> tracking_residual / l1 test_post_ci x100 |
| `\valResLoneOod` | 72.1 | OOD RMSE after 3 stages, cm | results/summary.json -> tracking_residual / l1 ood_post x100 |
| `\valResLoneOodCrash` | 52 | OOD crash rate after 3 stages, % | results/summary.json -> tracking_residual / l1 ood_crash |
| `\valResDrPre` | 7.3 | held-out RMSE before adapting, cm | results/summary.json -> tracking_residual / dr test_pre x100 |
| `\valResDrPost` | 7.3 | held-out RMSE after 3 stages, cm | results/summary.json -> tracking_residual / dr test_post x100 |
| `\valResDrCi` | 1.0 | 95% half-interval of held-out RMSE after adapting, cm | results/summary.json -> tracking_residual / dr test_post_ci x100 |
| `\valResDrOod` | 63.1 | OOD RMSE after 3 stages, cm | results/summary.json -> tracking_residual / dr ood_post x100 |
| `\valResDrOodCrash` | 44 | OOD crash rate after 3 stages, % | results/summary.json -> tracking_residual / dr ood_crash |
| `\valResDrftPre` | 7.3 | held-out RMSE before adapting, cm | results/summary.json -> tracking_residual / dr_finetune test_pre x100 |
| `\valResDrftPost` | 8.0 | held-out RMSE after 3 stages, cm | results/summary.json -> tracking_residual / dr_finetune test_post x100 |
| `\valResDrftCi` | 1.0 | 95% half-interval of held-out RMSE after adapting, cm | results/summary.json -> tracking_residual / dr_finetune test_post_ci x100 |
| `\valResDrftOod` | 63.6 | OOD RMSE after 3 stages, cm | results/summary.json -> tracking_residual / dr_finetune ood_post x100 |
| `\valResDrftOodCrash` | 43 | OOD crash rate after 3 stages, % | results/summary.json -> tracking_residual / dr_finetune ood_crash |
| `\valResMamlPre` | 8.7 | held-out RMSE before adapting, cm | results/summary.json -> tracking_residual / maml test_pre x100 |
| `\valResMamlPost` | 7.8 | held-out RMSE after 3 stages, cm | results/summary.json -> tracking_residual / maml test_post x100 |
| `\valResMamlCi` | 1.1 | 95% half-interval of held-out RMSE after adapting, cm | results/summary.json -> tracking_residual / maml test_post_ci x100 |
| `\valResMamlOod` | 70.8 | OOD RMSE after 3 stages, cm | results/summary.json -> tracking_residual / maml ood_post x100 |
| `\valResMamlOodCrash` | 49 | OOD crash rate after 3 stages, % | results/summary.json -> tracking_residual / maml ood_crash |
| `\valResFomamlPre` | 8.5 | held-out RMSE before adapting, cm | results/summary.json -> tracking_residual / fomaml test_pre x100 |
| `\valResFomamlPost` | 7.8 | held-out RMSE after 3 stages, cm | results/summary.json -> tracking_residual / fomaml test_post x100 |
| `\valResFomamlCi` | 1.0 | 95% half-interval of held-out RMSE after adapting, cm | results/summary.json -> tracking_residual / fomaml test_post_ci x100 |
| `\valResFomamlOod` | 66.9 | OOD RMSE after 3 stages, cm | results/summary.json -> tracking_residual / fomaml ood_post x100 |
| `\valResFomamlOodCrash` | 46 | OOD crash rate after 3 stages, % | results/summary.json -> tracking_residual / fomaml ood_crash |
| `\valResAnilPre` | 8.6 | held-out RMSE before adapting, cm | results/summary.json -> tracking_residual / anil test_pre x100 |
| `\valResAnilPost` | 7.7 | held-out RMSE after 3 stages, cm | results/summary.json -> tracking_residual / anil test_post x100 |
| `\valResAnilCi` | 1.1 | 95% half-interval of held-out RMSE after adapting, cm | results/summary.json -> tracking_residual / anil test_post_ci x100 |
| `\valResAnilOod` | 70.4 | OOD RMSE after 3 stages, cm | results/summary.json -> tracking_residual / anil ood_post x100 |
| `\valResAnilOodCrash` | 49 | OOD crash rate after 3 stages, % | results/summary.json -> tracking_residual / anil ood_crash |
| `\valResMetasgdPre` | 8.7 | held-out RMSE before adapting, cm | results/summary.json -> tracking_residual / metasgd test_pre x100 |
| `\valResMetasgdPost` | 7.8 | held-out RMSE after 3 stages, cm | results/summary.json -> tracking_residual / metasgd test_post x100 |
| `\valResMetasgdCi` | 1.1 | 95% half-interval of held-out RMSE after adapting, cm | results/summary.json -> tracking_residual / metasgd test_post_ci x100 |
| `\valResMetasgdOod` | 69.3 | OOD RMSE after 3 stages, cm | results/summary.json -> tracking_residual / metasgd ood_post x100 |
| `\valResMetasgdOodCrash` | 48 | OOD crash rate after 3 stages, % | results/summary.json -> tracking_residual / metasgd ood_crash |
| `\valResReptilePre` | 15.2 | held-out RMSE before adapting, cm | results/summary.json -> tracking_residual / reptile test_pre x100 |
| `\valResReptilePost` | 14.8 | held-out RMSE after 3 stages, cm | results/summary.json -> tracking_residual / reptile test_post x100 |
| `\valResReptileCi` | 2.0 | 95% half-interval of held-out RMSE after adapting, cm | results/summary.json -> tracking_residual / reptile test_post_ci x100 |
| `\valResReptileOod` | 68.6 | OOD RMSE after 3 stages, cm | results/summary.json -> tracking_residual / reptile ood_post x100 |
| `\valResReptileOodCrash` | 36 | OOD crash rate after 3 stages, % | results/summary.json -> tracking_residual / reptile ood_crash |
| `\valResPearlPre` | 10.5 | held-out RMSE before adapting, cm | results/summary.json -> tracking_residual / pearl test_pre x100 |
| `\valResPearlPost` | 9.0 | held-out RMSE after 3 stages, cm | results/summary.json -> tracking_residual / pearl test_post x100 |
| `\valResPearlCi` | 1.1 | 95% half-interval of held-out RMSE after adapting, cm | results/summary.json -> tracking_residual / pearl test_post_ci x100 |
| `\valResPearlOod` | 69.2 | OOD RMSE after 3 stages, cm | results/summary.json -> tracking_residual / pearl ood_post x100 |
| `\valResPearlOodCrash` | 49 | OOD crash rate after 3 stages, % | results/summary.json -> tracking_residual / pearl ood_crash |
| `\valResRltwoPre` | 18.4 | held-out RMSE before adapting, cm | results/summary.json -> tracking_residual / rl2 test_pre x100 |
| `\valResRltwoPost` | 17.4 | held-out RMSE after 3 stages, cm | results/summary.json -> tracking_residual / rl2 test_post x100 |
| `\valResRltwoCi` | 1.5 | 95% half-interval of held-out RMSE after adapting, cm | results/summary.json -> tracking_residual / rl2 test_post_ci x100 |
| `\valResRltwoOod` | 64.6 | OOD RMSE after 3 stages, cm | results/summary.json -> tracking_residual / rl2 ood_post x100 |
| `\valResRltwoOodCrash` | 36 | OOD crash rate after 3 stages, % | results/summary.json -> tracking_residual / rl2 ood_crash |
| `\valGainClassicalPre` | 21.5 | held-out RMSE before adapting, cm | results/summary.json -> tracking_gains / classical test_pre x100 |
| `\valGainClassicalPost` | 21.5 | held-out RMSE after 3 stages, cm | results/summary.json -> tracking_gains / classical test_post x100 |
| `\valGainClassicalCi` | 2.8 | 95% half-interval of held-out RMSE after adapting, cm | results/summary.json -> tracking_gains / classical test_post_ci x100 |
| `\valGainClassicalOod` | 79.0 | OOD RMSE after 3 stages, cm | results/summary.json -> tracking_gains / classical ood_post x100 |
| `\valGainClassicalOodCrash` | 34 | OOD crash rate after 3 stages, % | results/summary.json -> tracking_gains / classical ood_crash |
| `\valGainDrPre` | 14.5 | held-out RMSE before adapting, cm | results/summary.json -> tracking_gains / dr test_pre x100 |
| `\valGainDrPost` | 14.5 | held-out RMSE after 3 stages, cm | results/summary.json -> tracking_gains / dr test_post x100 |
| `\valGainDrCi` | 1.2 | 95% half-interval of held-out RMSE after adapting, cm | results/summary.json -> tracking_gains / dr test_post_ci x100 |
| `\valGainDrOod` | 77.4 | OOD RMSE after 3 stages, cm | results/summary.json -> tracking_gains / dr ood_post x100 |
| `\valGainDrOodCrash` | 53 | OOD crash rate after 3 stages, % | results/summary.json -> tracking_gains / dr ood_crash |
| `\valGainDrftPre` | 14.5 | held-out RMSE before adapting, cm | results/summary.json -> tracking_gains / dr_finetune test_pre x100 |
| `\valGainDrftPost` | 14.3 | held-out RMSE after 3 stages, cm | results/summary.json -> tracking_gains / dr_finetune test_post x100 |
| `\valGainDrftCi` | 1.2 | 95% half-interval of held-out RMSE after adapting, cm | results/summary.json -> tracking_gains / dr_finetune test_post_ci x100 |
| `\valGainDrftOod` | 75.4 | OOD RMSE after 3 stages, cm | results/summary.json -> tracking_gains / dr_finetune ood_post x100 |
| `\valGainDrftOodCrash` | 50 | OOD crash rate after 3 stages, % | results/summary.json -> tracking_gains / dr_finetune ood_crash |
| `\valGainMamlPre` | 15.9 | held-out RMSE before adapting, cm | results/summary.json -> tracking_gains / maml test_pre x100 |
| `\valGainMamlPost` | 12.8 | held-out RMSE after 3 stages, cm | results/summary.json -> tracking_gains / maml test_post x100 |
| `\valGainMamlCi` | 1.4 | 95% half-interval of held-out RMSE after adapting, cm | results/summary.json -> tracking_gains / maml test_post_ci x100 |
| `\valGainMamlOod` | 70.5 | OOD RMSE after 3 stages, cm | results/summary.json -> tracking_gains / maml ood_post x100 |
| `\valGainMamlOodCrash` | 44 | OOD crash rate after 3 stages, % | results/summary.json -> tracking_gains / maml ood_crash |
| `\valGainFomamlPre` | 15.9 | held-out RMSE before adapting, cm | results/summary.json -> tracking_gains / fomaml test_pre x100 |
| `\valGainFomamlPost` | 13.0 | held-out RMSE after 3 stages, cm | results/summary.json -> tracking_gains / fomaml test_post x100 |
| `\valGainFomamlCi` | 1.4 | 95% half-interval of held-out RMSE after adapting, cm | results/summary.json -> tracking_gains / fomaml test_post_ci x100 |
| `\valGainFomamlOod` | 73.1 | OOD RMSE after 3 stages, cm | results/summary.json -> tracking_gains / fomaml ood_post x100 |
| `\valGainFomamlOodCrash` | 47 | OOD crash rate after 3 stages, % | results/summary.json -> tracking_gains / fomaml ood_crash |
| `\valGainMetasgdPre` | 15.8 | held-out RMSE before adapting, cm | results/summary.json -> tracking_gains / metasgd test_pre x100 |
| `\valGainMetasgdPost` | 10.8 | held-out RMSE after 3 stages, cm | results/summary.json -> tracking_gains / metasgd test_post x100 |
| `\valGainMetasgdCi` | 1.1 | 95% half-interval of held-out RMSE after adapting, cm | results/summary.json -> tracking_gains / metasgd test_post_ci x100 |
| `\valGainMetasgdOod` | 69.3 | OOD RMSE after 3 stages, cm | results/summary.json -> tracking_gains / metasgd ood_post x100 |
| `\valGainMetasgdOodCrash` | 44 | OOD crash rate after 3 stages, % | results/summary.json -> tracking_gains / metasgd ood_crash |
| `\valGainReptilePre` | 13.6 | held-out RMSE before adapting, cm | results/summary.json -> tracking_gains / reptile test_pre x100 |
| `\valGainReptilePost` | 13.5 | held-out RMSE after 3 stages, cm | results/summary.json -> tracking_gains / reptile test_post x100 |
| `\valGainReptileCi` | 1.1 | 95% half-interval of held-out RMSE after adapting, cm | results/summary.json -> tracking_gains / reptile test_post_ci x100 |
| `\valGainReptileOod` | 75.8 | OOD RMSE after 3 stages, cm | results/summary.json -> tracking_gains / reptile ood_post x100 |
| `\valGainReptileOodCrash` | 53 | OOD crash rate after 3 stages, % | results/summary.json -> tracking_gains / reptile ood_crash |
| `\valNavClassicalPre` | 83 | held-out success before adapting, % | results/summary.json -> navigation / classical test_pre |
| `\valNavClassicalPost` | 83 | held-out success after 3 stages, % | results/summary.json -> navigation / classical test_post |
| `\valNavClassicalColl` | 14 | held-out collisions after 3 stages, % | results/summary.json -> navigation / classical test_collision |
| `\valNavClassicalOod` | 16 | OOD success after 3 stages, % | results/summary.json -> navigation / classical ood_post |
| `\valNavClassicalFullPre` | 73 | full-stack success before adapting, % | results/summary.json -> navigation / classical full_test_success_pre |
| `\valNavClassicalFullPost` | 73 | full-stack success after 1 stage, % | results/summary.json -> navigation / classical full_test_success_post |
| `\valNavClassicalFullColl` | 7 | full-stack collisions after 1 stage, % | results/summary.json -> navigation / classical full_test_collision_post |
| `\valNavClassicallonePre` | 77 | held-out success before adapting, % | results/summary.json -> navigation / classical_l1 test_pre |
| `\valNavClassicallonePost` | 77 | held-out success after 3 stages, % | results/summary.json -> navigation / classical_l1 test_post |
| `\valNavClassicalloneColl` | 21 | held-out collisions after 3 stages, % | results/summary.json -> navigation / classical_l1 test_collision |
| `\valNavClassicalloneOod` | 8 | OOD success after 3 stages, % | results/summary.json -> navigation / classical_l1 ood_post |
| `\valNavClassicalloneFullPre` | 73 | full-stack success before adapting, % | results/summary.json -> navigation / classical_l1 full_test_success_pre |
| `\valNavClassicalloneFullPost` | 73 | full-stack success after 1 stage, % | results/summary.json -> navigation / classical_l1 full_test_success_post |
| `\valNavClassicalloneFullColl` | 9 | full-stack collisions after 1 stage, % | results/summary.json -> navigation / classical_l1 full_test_collision_post |
| `\valNavDrPre` | 72 | held-out success before adapting, % | results/summary.json -> navigation / dr test_pre |
| `\valNavDrPost` | 72 | held-out success after 3 stages, % | results/summary.json -> navigation / dr test_post |
| `\valNavDrColl` | 28 | held-out collisions after 3 stages, % | results/summary.json -> navigation / dr test_collision |
| `\valNavDrOod` | 13 | OOD success after 3 stages, % | results/summary.json -> navigation / dr ood_post |
| `\valNavDrFullPre` | 44 | full-stack success before adapting, % | results/summary.json -> navigation / dr full_test_success_pre |
| `\valNavDrFullPost` | 44 | full-stack success after 1 stage, % | results/summary.json -> navigation / dr full_test_success_post |
| `\valNavDrFullColl` | 56 | full-stack collisions after 1 stage, % | results/summary.json -> navigation / dr full_test_collision_post |
| `\valNavDrftPre` | 72 | held-out success before adapting, % | results/summary.json -> navigation / dr_finetune test_pre |
| `\valNavDrftPost` | 71 | held-out success after 3 stages, % | results/summary.json -> navigation / dr_finetune test_post |
| `\valNavDrftColl` | 29 | held-out collisions after 3 stages, % | results/summary.json -> navigation / dr_finetune test_collision |
| `\valNavDrftOod` | 17 | OOD success after 3 stages, % | results/summary.json -> navigation / dr_finetune ood_post |
| `\valNavDrftFullPre` | 44 | full-stack success before adapting, % | results/summary.json -> navigation / dr_finetune full_test_success_pre |
| `\valNavDrftFullPost` | 50 | full-stack success after 1 stage, % | results/summary.json -> navigation / dr_finetune full_test_success_post |
| `\valNavDrftFullColl` | 50 | full-stack collisions after 1 stage, % | results/summary.json -> navigation / dr_finetune full_test_collision_post |
| `\valNavEtoePre` | 52 | held-out success before adapting, % | results/summary.json -> navigation / e2e_dr test_pre |
| `\valNavEtoePost` | 52 | held-out success after 3 stages, % | results/summary.json -> navigation / e2e_dr test_post |
| `\valNavEtoeColl` | 48 | held-out collisions after 3 stages, % | results/summary.json -> navigation / e2e_dr test_collision |
| `\valNavEtoeOod` | 10 | OOD success after 3 stages, % | results/summary.json -> navigation / e2e_dr ood_post |
| `\valNavEtoeFullPre` | 51 | full-stack success before adapting, % | results/summary.json -> navigation / e2e_dr full_test_success_pre |
| `\valNavEtoeFullPost` | 51 | full-stack success after 1 stage, % | results/summary.json -> navigation / e2e_dr full_test_success_post |
| `\valNavEtoeFullColl` | 49 | full-stack collisions after 1 stage, % | results/summary.json -> navigation / e2e_dr full_test_collision_post |
| `\valNavEtoeftPre` | 52 | held-out success before adapting, % | results/summary.json -> navigation / e2e_dr_finetune test_pre |
| `\valNavEtoeftPost` | 46 | held-out success after 3 stages, % | results/summary.json -> navigation / e2e_dr_finetune test_post |
| `\valNavEtoeftColl` | 54 | held-out collisions after 3 stages, % | results/summary.json -> navigation / e2e_dr_finetune test_collision |
| `\valNavEtoeftOod` | 16 | OOD success after 3 stages, % | results/summary.json -> navigation / e2e_dr_finetune ood_post |
| `\valNavEtoeftFullPre` | 51 | full-stack success before adapting, % | results/summary.json -> navigation / e2e_dr_finetune full_test_success_pre |
| `\valNavEtoeftFullPost` | 47 | full-stack success after 1 stage, % | results/summary.json -> navigation / e2e_dr_finetune full_test_success_post |
| `\valNavEtoeftFullColl` | 53 | full-stack collisions after 1 stage, % | results/summary.json -> navigation / e2e_dr_finetune full_test_collision_post |
| `\valNavMamlPre` | 73 | held-out success before adapting, % | results/summary.json -> navigation / maml test_pre |
| `\valNavMamlPost` | 36 | held-out success after 3 stages, % | results/summary.json -> navigation / maml test_post |
| `\valNavMamlColl` | 60 | held-out collisions after 3 stages, % | results/summary.json -> navigation / maml test_collision |
| `\valNavMamlOod` | 8 | OOD success after 3 stages, % | results/summary.json -> navigation / maml ood_post |
| `\valNavMamlFullPre` | 46 | full-stack success before adapting, % | results/summary.json -> navigation / maml full_test_success_pre |
| `\valNavMamlFullPost` | 32 | full-stack success after 1 stage, % | results/summary.json -> navigation / maml full_test_success_post |
| `\valNavMamlFullColl` | 67 | full-stack collisions after 1 stage, % | results/summary.json -> navigation / maml full_test_collision_post |
| `\valNavFomamlPre` | 76 | held-out success before adapting, % | results/summary.json -> navigation / fomaml test_pre |
| `\valNavFomamlPost` | 31 | held-out success after 3 stages, % | results/summary.json -> navigation / fomaml test_post |
| `\valNavFomamlColl` | 69 | held-out collisions after 3 stages, % | results/summary.json -> navigation / fomaml test_collision |
| `\valNavFomamlOod` | 5 | OOD success after 3 stages, % | results/summary.json -> navigation / fomaml ood_post |
| `\valNavFomamlFullPre` | 53 | full-stack success before adapting, % | results/summary.json -> navigation / fomaml full_test_success_pre |
| `\valNavFomamlFullPost` | 31 | full-stack success after 1 stage, % | results/summary.json -> navigation / fomaml full_test_success_post |
| `\valNavFomamlFullColl` | 69 | full-stack collisions after 1 stage, % | results/summary.json -> navigation / fomaml full_test_collision_post |
| `\valNavAnilPre` | 76 | held-out success before adapting, % | results/summary.json -> navigation / anil test_pre |
| `\valNavAnilPost` | 35 | held-out success after 3 stages, % | results/summary.json -> navigation / anil test_post |
| `\valNavAnilColl` | 65 | held-out collisions after 3 stages, % | results/summary.json -> navigation / anil test_collision |
| `\valNavAnilOod` | 8 | OOD success after 3 stages, % | results/summary.json -> navigation / anil ood_post |
| `\valNavAnilFullPre` | 49 | full-stack success before adapting, % | results/summary.json -> navigation / anil full_test_success_pre |
| `\valNavAnilFullPost` | 45 | full-stack success after 1 stage, % | results/summary.json -> navigation / anil full_test_success_post |
| `\valNavAnilFullColl` | 55 | full-stack collisions after 1 stage, % | results/summary.json -> navigation / anil full_test_collision_post |
| `\valNavMetasgdPre` | 71 | held-out success before adapting, % | results/summary.json -> navigation / metasgd test_pre |
| `\valNavMetasgdPost` | 49 | held-out success after 3 stages, % | results/summary.json -> navigation / metasgd test_post |
| `\valNavMetasgdColl` | 50 | held-out collisions after 3 stages, % | results/summary.json -> navigation / metasgd test_collision |
| `\valNavMetasgdOod` | 6 | OOD success after 3 stages, % | results/summary.json -> navigation / metasgd ood_post |
| `\valNavMetasgdFullPre` | 46 | full-stack success before adapting, % | results/summary.json -> navigation / metasgd full_test_success_pre |
| `\valNavMetasgdFullPost` | 48 | full-stack success after 1 stage, % | results/summary.json -> navigation / metasgd full_test_success_post |
| `\valNavMetasgdFullColl` | 51 | full-stack collisions after 1 stage, % | results/summary.json -> navigation / metasgd full_test_collision_post |
| `\valNavReptilePre` | 72 | held-out success before adapting, % | results/summary.json -> navigation / reptile test_pre |
| `\valNavReptilePost` | 71 | held-out success after 3 stages, % | results/summary.json -> navigation / reptile test_post |
| `\valNavReptileColl` | 29 | held-out collisions after 3 stages, % | results/summary.json -> navigation / reptile test_collision |
| `\valNavReptileOod` | 14 | OOD success after 3 stages, % | results/summary.json -> navigation / reptile ood_post |
| `\valNavReptileFullPre` | 46 | full-stack success before adapting, % | results/summary.json -> navigation / reptile full_test_success_pre |
| `\valNavReptileFullPost` | 47 | full-stack success after 1 stage, % | results/summary.json -> navigation / reptile full_test_success_post |
| `\valNavReptileFullColl` | 53 | full-stack collisions after 1 stage, % | results/summary.json -> navigation / reptile full_test_collision_post |
| `\valNavPearlPre` | 70 | held-out success before adapting, % | results/summary.json -> navigation / pearl test_pre |
| `\valNavPearlPost` | 71 | held-out success after 3 stages, % | results/summary.json -> navigation / pearl test_post |
| `\valNavPearlColl` | 26 | held-out collisions after 3 stages, % | results/summary.json -> navigation / pearl test_collision |
| `\valNavPearlOod` | 9 | OOD success after 3 stages, % | results/summary.json -> navigation / pearl ood_post |
| `\valNavPearlFullPre` | 50 | full-stack success before adapting, % | results/summary.json -> navigation / pearl full_test_success_pre |
| `\valNavPearlFullPost` | 55 | full-stack success after 1 stage, % | results/summary.json -> navigation / pearl full_test_success_post |
| `\valNavPearlFullColl` | 42 | full-stack collisions after 1 stage, % | results/summary.json -> navigation / pearl full_test_collision_post |
| `\valNavRltwoPre` | 60 | held-out success before adapting, % | results/summary.json -> navigation / rl2 test_pre |
| `\valNavRltwoPost` | 55 | held-out success after 3 stages, % | results/summary.json -> navigation / rl2 test_post |
| `\valNavRltwoColl` | 45 | held-out collisions after 3 stages, % | results/summary.json -> navigation / rl2 test_collision |
| `\valNavRltwoOod` | 8 | OOD success after 3 stages, % | results/summary.json -> navigation / rl2 ood_post |
| `\valNavRltwoFullPre` | 34 | full-stack success before adapting, % | results/summary.json -> navigation / rl2 full_test_success_pre |
| `\valNavRltwoFullPost` | 39 | full-stack success after 1 stage, % | results/summary.json -> navigation / rl2 full_test_success_post |
| `\valNavRltwoFullColl` | 60 | full-stack collisions after 1 stage, % | results/summary.json -> navigation / rl2 full_test_collision_post |
| `\valTaskMassTrainLo` | 0.85 | mass_scale train range low | drone_autonomy/tasks.py RANGES |
| `\valTaskMassTrainHi` | 1.30 | mass_scale train range high | drone_autonomy/tasks.py RANGES |
| `\valTaskMassOodLo` | 1.30 | mass_scale ood range low | drone_autonomy/tasks.py RANGES |
| `\valTaskMassOodHi` | 1.40 | mass_scale ood range high | drone_autonomy/tasks.py RANGES |
| `\valTaskMotorTrainLo` | 75 | motor_eff_min train range low | drone_autonomy/tasks.py RANGES |
| `\valTaskMotorTrainHi` | 100 | motor_eff_min train range high | drone_autonomy/tasks.py RANGES |
| `\valTaskMotorOodLo` | 65 | motor_eff_min ood range low | drone_autonomy/tasks.py RANGES |
| `\valTaskMotorOodHi` | 75 | motor_eff_min ood range high | drone_autonomy/tasks.py RANGES |
| `\valTaskDragTrainLo` | 0.5 | drag_scale train range low | drone_autonomy/tasks.py RANGES |
| `\valTaskDragTrainHi` | 2.0 | drag_scale train range high | drone_autonomy/tasks.py RANGES |
| `\valTaskDragOodLo` | 2.0 | drag_scale ood range low | drone_autonomy/tasks.py RANGES |
| `\valTaskDragOodHi` | 3.0 | drag_scale ood range high | drone_autonomy/tasks.py RANGES |
| `\valTaskWindTrainLo` | 0.0 | wind_speed train range low | drone_autonomy/tasks.py RANGES |
| `\valTaskWindTrainHi` | 2.5 | wind_speed train range high | drone_autonomy/tasks.py RANGES |
| `\valTaskWindOodLo` | 2.5 | wind_speed ood range low | drone_autonomy/tasks.py RANGES |
| `\valTaskWindOodHi` | 4.0 | wind_speed ood range high | drone_autonomy/tasks.py RANGES |
| `\valTaskGustTrainLo` | 0.0 | gust_std train range low | drone_autonomy/tasks.py RANGES |
| `\valTaskGustTrainHi` | 0.8 | gust_std train range high | drone_autonomy/tasks.py RANGES |
| `\valTaskGustOodLo` | 0.8 | gust_std ood range low | drone_autonomy/tasks.py RANGES |
| `\valTaskGustOodHi` | 1.5 | gust_std ood range high | drone_autonomy/tasks.py RANGES |
| `\valTaskLatTrainLo` | 0 | latency_steps train range low | drone_autonomy/tasks.py RANGES |
| `\valTaskLatTrainHi` | 30 | latency_steps train range high | drone_autonomy/tasks.py RANGES |
| `\valTaskLatOodLo` | 30 | latency_steps ood range low | drone_autonomy/tasks.py RANGES |
| `\valTaskLatOodHi` | 50 | latency_steps ood range high | drone_autonomy/tasks.py RANGES |
| `\valResRatioClassical` | 2.9 | RMSE ratio classical / DR residual | summary.json tracking_residual classical.test_post / dr.test_post |
| `\valResRatioLone` | 2.1 | RMSE ratio L1 / DR residual | summary.json tracking_residual l1.test_post / dr.test_post |
| `\valResOodCrashLearnedLo` | 43 | lowest OOD crash rate among learned residuals (excl. Reptile, RL2), % | summary.json min ood_crash over dr,dr_finetune,maml,fomaml,anil,metasgd,pearl |
| `\valResOodCrashLearnedHi` | 49 | highest OOD crash rate among learned residuals, % | summary.json max ood_crash over same set |
| `\valOodRmseMin` | 63.1 | lowest OOD RMSE of any tracking method, cm | summary.json min ood_post over tracking problems |
| `\valOodAdaptMaxDelta` | 7 | largest change in OOD RMSE from adapting (any adaptive tracking method), cm | summary.json max |ood_post - ood_pre| over tracking methods with ood_episodes > 0 |
| `\valNavOodMax` | 17 | highest OOD success of any navigation method, % | summary.json max navigation ood_post |
| `\valNavFullLearnedLo` | 31 | lowest full-stack success, learned planners, % | summary.json min full_test_success_post |
| `\valNavFullLearnedHi` | 55 | highest full-stack success, learned planners, % | summary.json max full_test_success_post |
| `\valNavFullCollLo` | 42 | lowest full-stack collision rate, learned planners, % | summary.json min full_test_collision_post |
| `\valNavFullCollHi` | 69 | highest full-stack collision rate, learned planners, % | summary.json max full_test_collision_post |
| `\valNavAnilStageOne` | 53 | held-out success after 1 adaptation stage, % | results/summary.json -> navigation / anil test_curve[1] |
| `\valNavDrftStageOne` | 72 | held-out success after 1 adaptation stage, % | results/summary.json -> navigation / dr_finetune test_curve[1] |
| `\valNavEtoeftStageOne` | 49 | held-out success after 1 adaptation stage, % | results/summary.json -> navigation / e2e_dr_finetune test_curve[1] |
| `\valNavFomamlStageOne` | 50 | held-out success after 1 adaptation stage, % | results/summary.json -> navigation / fomaml test_curve[1] |
| `\valNavMamlStageOne` | 46 | held-out success after 1 adaptation stage, % | results/summary.json -> navigation / maml test_curve[1] |
| `\valNavMetasgdStageOne` | 67 | held-out success after 1 adaptation stage, % | results/summary.json -> navigation / metasgd test_curve[1] |
| `\valNavPearlStageOne` | 71 | held-out success after 1 adaptation stage, % | results/summary.json -> navigation / pearl test_curve[1] |
| `\valNavReptileStageOne` | 70 | held-out success after 1 adaptation stage, % | results/summary.json -> navigation / reptile test_curve[1] |
| `\valNavRltwoStageOne` | 58 | held-out success after 1 adaptation stage, % | results/summary.json -> navigation / rl2 test_curve[1] |
| `\valStepsResDr` | 9.6 | tracking_residual dr training budget, million env steps | methods.py ITERS[tracking_residual][dr] x figures_scripts/common.py EPISODES_PER_ITER x HORIZON |
| `\valStepsResMaml` | 9.6 | tracking_residual maml training budget, million env steps | methods.py ITERS[tracking_residual][maml] x figures_scripts/common.py EPISODES_PER_ITER x HORIZON |
| `\valStepsResReptile` | 11.5 | tracking_residual reptile training budget, million env steps | methods.py ITERS[tracking_residual][reptile] x figures_scripts/common.py EPISODES_PER_ITER x HORIZON |
| `\valStepsResPearl` | 1.0 | tracking_residual pearl training budget, million env steps | methods.py ITERS[tracking_residual][pearl] x figures_scripts/common.py EPISODES_PER_ITER x HORIZON |
| `\valStepsResRltwo` | 4.3 | tracking_residual rl2 training budget, million env steps | methods.py ITERS[tracking_residual][rl2] x figures_scripts/common.py EPISODES_PER_ITER x HORIZON |
| `\valStepsGainDr` | 4.8 | tracking_gains dr training budget, million env steps | methods.py ITERS[tracking_gains][dr] x figures_scripts/common.py EPISODES_PER_ITER x HORIZON |
| `\valStepsGainMaml` | 6.4 | tracking_gains maml training budget, million env steps | methods.py ITERS[tracking_gains][maml] x figures_scripts/common.py EPISODES_PER_ITER x HORIZON |
| `\valStepsGainReptile` | 7.7 | tracking_gains reptile training budget, million env steps | methods.py ITERS[tracking_gains][reptile] x figures_scripts/common.py EPISODES_PER_ITER x HORIZON |
| `\valStepsNavDr` | 12.0 | navigation dr training budget, million env steps | methods.py ITERS[navigation][dr] x figures_scripts/common.py EPISODES_PER_ITER x HORIZON |
| `\valStepsNavMaml` | 5.8 | navigation maml training budget, million env steps | methods.py ITERS[navigation][maml] x figures_scripts/common.py EPISODES_PER_ITER x HORIZON |
| `\valStepsNavReptile` | 7.2 | navigation reptile training budget, million env steps | methods.py ITERS[navigation][reptile] x figures_scripts/common.py EPISODES_PER_ITER x HORIZON |
| `\valStepsNavPearl` | 1.0 | navigation pearl training budget, million env steps | methods.py ITERS[navigation][pearl] x figures_scripts/common.py EPISODES_PER_ITER x HORIZON |
| `\valStepsNavRltwo` | 5.2 | navigation rl2 training budget, million env steps | methods.py ITERS[navigation][rl2] x figures_scripts/common.py EPISODES_PER_ITER x HORIZON |
| `\valSeedsRes` | 2 | training seeds per learned method, tracking_residual | results/summary.json -> tracking_residual seeds |
| `\valSeedsGain` | 5 | training seeds per learned method, tracking_gains | results/summary.json -> tracking_gains seeds |
| `\valSeedsNav` | 2 | training seeds per learned method, navigation | results/summary.json -> navigation seeds |
| `\valNavFullRooms` | 48 | unseen rooms per seed, full-stack evaluation | drone_autonomy/benchmark.py FULLSTACK_TASKS['test'] |
| `\valNavFullFlights` | 96 | full-stack evaluation flights per method (rooms x seeds) | benchmark.py FULLSTACK_TASKS['test'] x seeds in results/navigation |
| `\valNavPrivRooms` | 96 | distinct unseen rooms per seed, privileged-planner evaluation (tasks x 4 episodes) | benchmark.py N_TASKS['navigation'] x E_eval=4 |
| `\valGainPairedDiff` | 3.5 | Meta-SGD minus DR+fine-tune held-out RMSE, mean paired improvement, cm | results/tracking_gains/{metasgd,dr_finetune}_seed*.json test[-1].rmse; paired by seed and task; 10,000 bootstrap resamples (rng seed 0) |
| `\valGainPairedLo` | 2.8 | paired improvement, 95% bootstrap CI lower end, cm | results/tracking_gains/{metasgd,dr_finetune}_seed*.json test[-1].rmse; paired by seed and task; 10,000 bootstrap resamples (rng seed 0) |
| `\valGainPairedHi` | 4.3 | paired improvement, 95% bootstrap CI upper end, cm | results/tracking_gains/{metasgd,dr_finetune}_seed*.json test[-1].rmse; paired by seed and task; 10,000 bootstrap resamples (rng seed 0) |
| `\valGainPairedWin` | 83 | share of task-seed pairs where Meta-SGD has lower RMSE, % | results/tracking_gains/{metasgd,dr_finetune}_seed*.json test[-1].rmse; paired by seed and task; 10,000 bootstrap resamples (rng seed 0) |
| `\valGainPairedN` | 160 | number of task-seed pairs in the paired comparison | results/tracking_gains/{metasgd,dr_finetune}_seed*.json test[-1].rmse; paired by seed and task; 10,000 bootstrap resamples (rng seed 0) |
| `\valLoneTunedTest` | 14.0 | tuned L1 held-out RMSE, cm | ideas/experiments/05_l1_tuning/results/l1_tuning.json tuned_test_rmse |
| `\valLoneDefaultTest` | 14.9 | default L1 held-out RMSE on the same episodes, cm | l1_tuning.json default_test_rmse |
| `\valLoneTunedCutoff` | 40 | tuned L1 filter bandwidth, rad/s | l1_tuning.json best.cutoff |
| `\valLoneTunedPole` | 10 | tuned L1 predictor pole, 1/s | l1_tuning.json best.a_s |
| `\valStepMamlOnePre` | 69 | I-02 maml step x1.0, 10 ep/stage: success before adapting, % | ideas/experiments/02_nav_step_size/results/maml_scale1.0_E10.json success[0] |
| `\valStepMamlOnePost` | 25 | I-02 maml step x1.0, 10 ep/stage: success after 3 stages, % | maml_scale1.0_E10.json success[3] |
| `\valStepMamlTenthPre` | 69 | I-02 maml step x0.1, 10 ep/stage: success before adapting, % | ideas/experiments/02_nav_step_size/results/maml_scale0.1_E10.json success[0] |
| `\valStepMamlTenthPost` | 72 | I-02 maml step x0.1, 10 ep/stage: success after 3 stages, % | maml_scale0.1_E10.json success[3] |
| `\valStepMamlThirdPre` | 69 | I-02 maml step x0.3, 10 ep/stage: success before adapting, % | ideas/experiments/02_nav_step_size/results/maml_scale0.3_E10.json success[0] |
| `\valStepMamlThirdPost` | 66 | I-02 maml step x0.3, 10 ep/stage: success after 3 stages, % | maml_scale0.3_E10.json success[3] |
| `\valStepMamlDataPre` | 69 | I-02 maml step x1.0, 30 ep/stage: success before adapting, % | ideas/experiments/02_nav_step_size/results/maml_scale1.0_E30.json success[0] |
| `\valStepMamlDataPost` | 64 | I-02 maml step x1.0, 30 ep/stage: success after 3 stages, % | maml_scale1.0_E30.json success[3] |
| `\valStepMetasgdOnePre` | 67 | I-02 metasgd step x1.0, 10 ep/stage: success before adapting, % | ideas/experiments/02_nav_step_size/results/metasgd_scale1.0_E10.json success[0] |
| `\valStepMetasgdOnePost` | 38 | I-02 metasgd step x1.0, 10 ep/stage: success after 3 stages, % | metasgd_scale1.0_E10.json success[3] |
| `\valStepMetasgdTenthPre` | 67 | I-02 metasgd step x0.1, 10 ep/stage: success before adapting, % | ideas/experiments/02_nav_step_size/results/metasgd_scale0.1_E10.json success[0] |
| `\valStepMetasgdTenthPost` | 70 | I-02 metasgd step x0.1, 10 ep/stage: success after 3 stages, % | metasgd_scale0.1_E10.json success[3] |
| `\valMildClassicalRmse` | 61.5 | mild-OOD RMSE, classical, cm | ideas/experiments/06_mild_ood/results mean over seeds rmse[-1] |
| `\valMildClassicalCrash` | 9 | mild-OOD crash rate, classical, % | 06_mild_ood crashed[-1] |
| `\valMildDrRmse` | 41.1 | mild-OOD RMSE, DR residual, cm | 06_mild_ood dr rmse[-1] |
| `\valMildResidCrashLo` | 14 | mild-OOD crash rate, lowest of DR/MAML-family residuals, % | 06_mild_ood min over dr,maml,fomaml,anil,metasgd |
| `\valMildResidCrashHi` | 18 | mild-OOD crash rate, highest of DR/MAML-family residuals, % | 06_mild_ood max over same set |

## Tables and figures

| Output | Script | Data |
|---|---|---|
| generated/tables/tracking.tex | figures_scripts/tracking_table.py | results/summary.json |
| generated/tables/navigation.tex | figures_scripts/navigation_table.py | results/summary.json |
| generated/tables/tasks.tex | figures_scripts/task_table.py | drone_autonomy/tasks.py RANGES |
| generated/tables/budget.tex | figures_scripts/budget_table.py | drone_autonomy/methods.py ITERS, common.py budget constants |
| generated/tables/stepsize.tex | figures_scripts/step_size_table.py | ideas/experiments/02_nav_step_size/results/*.json |
| figures/adaptation_curves.pdf | figures_scripts/adaptation_curves.py | results/<problem>/*_seed*.json |
| figures/example_flights.pdf | figures_scripts/example_flights.py | website/data/demo.json |

## Fixed settings quoted in the text

| Literal | Meaning | Where it is set |
|---|---|---|
| 500 | physics rate, Hz (physics_dt 0.002 s) | drone_autonomy/config.py Timing.physics_dt |
| 100 | classical controller rate, Hz | drone_autonomy/config.py Timing.control_dt |
| 50 | residual policy rate, Hz | drone_autonomy/config.py Timing.tracking_policy_dt |
| 10 | local planner rate, Hz; also exploratory episodes per adaptation stage (E=10) | config.py nav_policy_dt; benchmark.py bench_one E=10 |
| 2.0 | platform mass, kg | drone_autonomy/config.py Platform.mass |
| 0.25 | arm length, m | drone_autonomy/config.py Platform.arm_length |
| 0.0217 | Ixx = Iyy, kg m^2 (PX4 x500 model) | drone_autonomy/config.py Platform.inertia |
| 0.040 | Izz, kg m^2 (PX4 x500 model) | drone_autonomy/config.py Platform.inertia |
| 2.1 | thrust-to-weight ratio (estimate) | drone_autonomy/config.py Platform.thrust_to_weight |
| 40 | motor time constant, ms (estimate) | drone_autonomy/config.py Platform.motor_tau |
| 0.3 | linear drag, N s/m (estimate) | drone_autonomy/config.py Platform.drag_coeff |
| 35 | max tilt, degrees | drone_autonomy/config.py Platform.max_tilt_deg |
| 0.2 | voxel size, m | drone_autonomy/envs/navigation.py RES |
| 1.5 | carrot lookahead, m; crash threshold for tracking error, m | envs/navigation.py LOOKAHEAD; envs/tracking.py CRASH_ERR |
| 0.35 | drone collision radius, m | drone_autonomy/world.py DRONE_RADIUS |
| 0.15 | planning clearance margin, m | drone_autonomy/envs/navigation.py CLEARANCE |
| 87 | depth camera horizontal FOV, degrees | drone_autonomy/perception.py DepthCamera.hfov_deg |
| 58 | depth camera vertical FOV, degrees | drone_autonomy/perception.py DepthCamera.vfov_deg |
| 5 | depth camera max range, m | drone_autonomy/perception.py DepthCamera.max_range |
| 16 | policy depth image columns | drone_autonomy/perception.py DepthCamera.cols |
| 8 | policy depth image rows | drone_autonomy/perception.py DepthCamera.rows |
| 0.008 | depth noise coefficient (std = 0.008 d^2) | drone_autonomy/perception.py noise_quad |
| 14 | room length, m | drone_autonomy/world.py ROOM |
| 3 | room height, m; adaptation stages; RL^2 trial length in episodes | world.py ROOM; benchmark.py stages=3; rl2.py K=3 |
| 30 | navigation episode length, s; adaptation episodes after 3 stages | envs/navigation.py horizon=300 at 10 Hz; 3 x E=10 |
| 4 | tracking episode length, s (200 steps at 50 Hz) | drone_autonomy/envs/tracking.py horizon=200 |
| 1.9 | lowest hanging-obstacle height, m | drone_autonomy/world.py generate |
| 32 | held-out / OOD tasks per split, tracking | drone_autonomy/benchmark.py N_TASKS |
| 24 | held-out / OOD tasks per split, navigation (privileged planner) | drone_autonomy/benchmark.py N_TASKS |
| 12 | rooms per split, full-stack navigation | drone_autonomy/benchmark.py FULLSTACK_TASKS |
| 128 | worlds per training / test pool | drone_autonomy/rl/nav_problem.py pool_size |
| 16 | meta-batch tasks per iteration (gradient methods) | drone_autonomy/rl/meta/gradient.py meta_batch=16 |
| 0.1 | MAML-family inner learning rate | drone_autonomy/rl/meta/gradient.py inner_lr=0.1 |
| 3e-3 | Adam step for per-task PPO adaptation, tracking | drone_autonomy/methods.py INNER_LR default |
| 3e-4 | Adam step for per-task PPO adaptation, navigation | drone_autonomy/methods.py INNER_LR |
| 2 | training seeds, tracking | runs/tracking_*/<method>/seed0, seed1 |
| 1 | training seeds, navigation | runs/navigation/<method>/seed0 |
| 7 | number of controller gains / meta-learning algorithms | config.py Gains.NAMES; methods.py TRAINED |
| 95 | interval level, % | drone_autonomy/figures.py curve (1.96 standard errors) |
| 10 | reduction factor of the navigation inner step (3e-3 -> 3e-4) | drone_autonomy/methods.py INNER_LR |
| 12.5 | PX4 x500 model motor time constant up, ms (cited for comparison) | docs/DRONE-SELECTION.md |
| 67 | Jetson Orin Nano Super, TOPS | docs/DRONE-SELECTION.md (NVIDIA) |
| 1.6 | build cost lower bound, k USD (estimate) | docs/DRONE-SELECTION.md |
| 0.5 | goal tolerance, m | drone_autonomy/envs/navigation.py GOAL_TOL |
| 2.5 | upper wind speed in training range, m/s | drone_autonomy/tasks.py RANGES |
| 26 | A* neighbourhood (26-connected voxel grid) | drone_autonomy/planning.py NEIGH |
| 48 | mapping depth image columns | drone_autonomy/envs/navigation.py map_cam cols=48 |
| 24 | mapping depth image rows | drone_autonomy/envs/navigation.py map_cam rows=24 |
| 2026-10-05 | date platform prices and stock were checked (also '05') | docs/DRONE-SELECTION.md research date |
| 37 | Crazyflie 2.1 Brushless mass with guards, g | docs/DRONE-SELECTION.md [Bitcraze product page] |
| 285 | ModalAI Starling 2 takeoff mass, g | docs/DRONE-SELECTION.md [ModalAI datasheet] |
| 566 | ModalAI Starling 2 Max takeoff mass, g | docs/DRONE-SELECTION.md [ModalAI datasheet] |
| 893 | Holybro PX4 Vision V1.5 mass without battery, g | docs/DRONE-SELECTION.md [Holybro product page] |
| 2.0 | X500 build mass, kg (estimate; also PX4 x500 model mass) | docs/DRONE-SELECTION.md |
| 1.6--2.0 | X500 build cost range, k USD (estimate) | docs/DRONE-SELECTION.md |
| 70 | tilt limit for early termination, degrees | drone_autonomy/envs/tracking.py CRASH_TILT |
| 0.25 | reward length scale exp(-e/0.25), m; residual thrust bound (25% of hover) | drone_autonomy/envs/tracking.py reward, RESID_THRUST |
| 25 | residual thrust bound, % of hover thrust | drone_autonomy/envs/tracking.py RESID_THRUST |
| 15 | share of tracking episodes that are pure hover, % | drone_autonomy/envs/tracking.py _sample_refs |
| 0.5 | yaw-rate residual bound, rad/s; gust correlation time, s | envs/tracking.py RESID_RATE; dynamics.py GUST_TAU |
| 64 | tracking policy hidden units | drone_autonomy/rl/problems.py hidden=(64, 64) |
| 128 | navigation policy first hidden layer / RL2 GRU units / pool size | rl/nav_problem.py hidden; rl/meta/rl2.py hidden |
| 1--3 | price band of the platform search, k USD | drone_autonomy.md (user answer) |
| 9980 | CPU model Intel Core i9-9980HK | machine used for all runs (sysctl machdep.cpu.brand_string) |
| 435 | camera model RealSense D435i | docs/DRONE-SELECTION.md |
| 16 | held-out tasks in the step-size experiment (I-02) | ideas/experiments/02_nav_step_size/run.py fixed_eval_tasks(16) |
| 29 | Starling 2 Max configuration C29 (the one with ToF) | docs/DRONE-SELECTION.md |
