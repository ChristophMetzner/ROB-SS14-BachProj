#include <stdio.h>
#include "hocdec.h"
extern int nrnmpi_myid;
extern int nrn_nobanner_;
modl_reg(){
  if (!nrn_nobanner_) if (nrnmpi_myid < 1) {
    fprintf(stderr, "Additional mechanisms from files\n");

    fprintf(stderr," CurrentClampExt.mod");
    fprintf(stderr," ar.mod");
    fprintf(stderr," cad.mod");
    fprintf(stderr," cal.mod");
    fprintf(stderr," cat.mod");
    fprintf(stderr," k2.mod");
    fprintf(stderr," ka.mod");
    fprintf(stderr," ka_ib.mod");
    fprintf(stderr," kahp_deeppyr.mod");
    fprintf(stderr," kc.mod");
    fprintf(stderr," kdr.mod");
    fprintf(stderr," km.mod");
    fprintf(stderr," naf.mod");
    fprintf(stderr," nap.mod");
    fprintf(stderr, "\n");
  }
  _CurrentClampExt_reg();
  _ar_reg();
  _cad_reg();
  _cal_reg();
  _cat_reg();
  _k2_reg();
  _ka_reg();
  _ka_ib_reg();
  _kahp_deeppyr_reg();
  _kc_reg();
  _kdr_reg();
  _km_reg();
  _naf_reg();
  _nap_reg();
}
