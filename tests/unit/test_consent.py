import pytest
from core.conversation import _user_consented


class TestUserConsented:
    """Testa o matcher flexível de consentimento LGPD."""

    # Casos que DEVEM ser aceitos
    def test_aceita_sim(self):
        assert _user_consented("sim") is True

    def test_aceita_sim_com_espaco(self):
        assert _user_consented("  sim  ") is True

    def test_aceita_ok(self):
        assert _user_consented("ok") is True

    def test_aceita_ta_bom(self):
        assert _user_consented("tá bom") is True

    def test_aceita_ta_bom_sem_acento(self):
        assert _user_consented("ta bom") is True

    def test_aceita_claro(self):
        assert _user_consented("claro") is True

    def test_aceita_pode_ser(self):
        assert _user_consented("pode ser") is True

    def test_aceita_aceito(self):
        assert _user_consented("aceito") is True

    def test_aceita_aceito_os_termos(self):
        assert _user_consented("aceito os termos") is True

    def test_aceita_concordo(self):
        assert _user_consented("concordo") is True

    def test_aceita_sim_aceito(self):
        assert _user_consented("sim aceito") is True

    def test_aceita_s_minusculo(self):
        assert _user_consented("s") is True

    def test_aceita_yes(self):
        assert _user_consented("yes") is True

    def test_aceita_tudo_bem(self):
        assert _user_consented("tudo bem") is True

    def test_aceita_pode(self):
        assert _user_consented("pode") is True

    def test_aceita_positivo(self):
        assert _user_consented("positivo") is True

    def test_aceita_aceitei(self):
        # Começa com 'ac' então deve ser aceito
        assert _user_consented("aceitei sim") is True

    # Casos que NÃO devem ser aceitos
    def test_rejeita_nao(self):
        assert _user_consented("não") is False

    def test_rejeita_recuso(self):
        assert _user_consented("recuso") is False

    def test_rejeita_quero_saber_mais(self):
        assert _user_consented("quero saber mais antes") is False

    def test_rejeita_mensagem_vazia(self):
        assert _user_consented("") is False

    def test_rejeita_pergunta_generica(self):
        assert _user_consented("oi, tudo bem?") is False

    def test_rejeita_numero(self):
        assert _user_consented("42") is False
