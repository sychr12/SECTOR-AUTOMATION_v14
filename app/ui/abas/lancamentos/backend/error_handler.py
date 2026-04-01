import traceback


def tratar_erro(e: Exception) -> str:
    erro_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))

    # Detectar import circular
    if isinstance(e, ImportError) and "circular import" in str(e).lower():
        return (
            "⚠️ ERRO DE IMPORTAÇÃO CIRCULAR DETECTADO!\n\n"
            f"{erro_str}"
        )

    return f"❌ ERRO:\n\n{erro_str}"