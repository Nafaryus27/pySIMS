class MassSpectrum(Crater):
    def __init__(self, path: str):
        super().__init__(self, path)
        mass = self._raw_data["1"][_MASS] + self._raw_data["101"][_MASS]
        intens = self._raw_data["1"][_INTENSITY] + self._raw_data["101"][_INTENSITY]
        self._raw_data[_MASS] = mass 
        self._raw_data[_INTENSITY] = intens
       

    @property
    def mass(self) :
        return self.get_attr(_MASS)
    
    @property
    def intensity(self) :
        return self.get_attr(_INTENSITY)

    


def MassSpectrum_local_max(data: MassSpectrum, m_ref, n=32, DEBUG=False):
    # returns the intensity of the mass spectrum around m_ref (+/- 0.5 at. unit)
    idx = int(data.mass.index(m_ref) - n / 2)
    if DEBUG:
        print("Integer mass " + str(m_ref) + " located at index " + str(idx))
    local_spectrum = data.intensity[idx : idx + n]
    localmax_i = max(local_spectrum)
    if DEBUG:
        print("exp. intensity local max. intensity " + str(localmax_i))
    localmax_m = data.mass[local_spectrum.index(localmax_i) + idx]
    return localmax_m, localmax_i



def deviation_to_natural_abundance(data: MassSpectrum, ref, table_iso, n=32, PRINT=False):
    names_iso, masses_iso, abondances_iso = table_iso
    int_mass, elem = read_isotope_reference(ref)
    relevance_threshold = 100

    # calcul les rapports isotopiques naturels
    minors = []  # other isotopes than reference
    for iso in names_iso:
        if elem in iso:
            if iso != ref:
                minors.append(iso)
    if PRINT:
        print(minors)

    # reference abundance
    idx = names_iso.index(ref)
    ref_intens_theo = abondances_iso[idx]
    ref_int_mass_expe, ref_intens_expe = MassSpectrum_local_max(
        data, int_mass, n=n, DEBUG=PRINT
    )

    var_ionic_interference = 0
    if PRINT:
        print(ref, ref_intens_theo, ref_intens_expe)
    if ref_intens_expe > relevance_threshold:
        for minor in minors:
            idx = names_iso.index(minor)
            minor_int_mass_theo = masses_iso[idx]
            minor_intens_theo = abondances_iso[idx]
            minor_int_mass_expe, minor_intens_expe = MassSpectrum_local_max(
                data, np.round(minor_int_mass_theo), n=n, DEBUG=PRINT
            )
            r_theo = minor_intens_theo / ref_intens_theo
            r_expe = minor_intens_expe / ref_intens_expe
            if PRINT:
                print(minor, minor_intens_theo, minor_intens_expe)
            if PRINT:
                print(f" : r_theo = {r_theo:.2e}" + f" : r_expe = {r_expe:.2e}")
            var_ionic_interference += ((r_expe - r_theo) / r_theo) ** 2
            if PRINT:
                print((r_expe - r_theo) / r_theo)

        sigma_ionic_interference = np.sqrt(var_ionic_interference / len(minors))
    else:
        sigma_ionic_interference = -1
    if PRINT:
        print(f"std dev = {sigma_ionic_interference * 100:.1f} %")
    return sigma_ionic_interference