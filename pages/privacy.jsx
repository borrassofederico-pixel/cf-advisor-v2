export default function Privacy() {
  return (
    <main
      style={{
        maxWidth: 760,
        margin: "0 auto",
        padding: "48px 24px",
        fontFamily: "Outfit, system-ui, -apple-system, sans-serif",
        color: "#1a1a1a",
        lineHeight: 1.6,
      }}
    >
      <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: 34 }}>
        Informativa sulla Privacy
      </h1>
      <p style={{ color: "#666" }}>Ultimo aggiornamento: luglio 2026</p>

      <h2>1. Titolare del trattamento</h2>
      <p>
        Federico Borrasso, Consulente Finanziario. Per qualsiasi richiesta
        relativa al trattamento dei dati:{" "}
        <a href="mailto:borrassofederico@gmail.com">
          borrassofederico@gmail.com
        </a>
        .
      </p>

      <h2>2. Finalità e ambito</h2>
      <p>
        Questa applicazione è uno strumento personale di automazione per la
        pubblicazione di contenuti editoriali sui profili e sulle pagine social
        (LinkedIn, Instagram) di cui il titolare è proprietario o
        amministratore. L'applicazione non raccoglie, memorizza né condivide
        dati personali di terzi.
      </p>

      <h2>3. Dati trattati</h2>
      <p>
        L'applicazione utilizza esclusivamente i token di accesso rilasciati
        dalle piattaforme social, per conto del titolare, al solo scopo di
        pubblicare i contenuti da lui approvati. I token sono conservati in modo
        sicuro come segreti cifrati e non sono accessibili a terzi.
      </p>

      <h2>4. Condivisione con terzi</h2>
      <p>
        Nessun dato personale viene ceduto o venduto a terze parti. Le uniche
        comunicazioni avvengono con le API ufficiali delle piattaforme social
        per la pubblicazione dei contenuti.
      </p>

      <h2>5. Diritti dell'interessato</h2>
      <p>
        In conformità al GDPR (Reg. UE 2016/679), è possibile richiedere in
        qualsiasi momento l'accesso, la rettifica o la cancellazione dei propri
        dati scrivendo all'indirizzo indicato al punto 1.
      </p>

      <h2>6. Modifiche</h2>
      <p>
        La presente informativa può essere aggiornata nel tempo. Eventuali
        modifiche saranno pubblicate su questa pagina.
      </p>
    </main>
  );
}
