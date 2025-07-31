' Diccionario para convertir números escritos a números enteros

fechaEntrada="UNO DE MARZO DE DOS MIL VEINTICINTO"

Dim numeros As New Dictionary(Of String, String) From {
    {"UNO", "01"}, {"DOS", "02"}, {"TRES", "03"}, {"CUATRO", "04"},
    {"CINCO", "05"}, {"SEIS", "06"}, {"SIETE", "07"}, {"OCHO", "08"},
    {"NUEVE", "09"}, {"DIEZ", "10"}, {"ONCE", "11"}, {"DOCE", "12"},
    {"TRECE", "13"}, {"CATORCE", "14"}, {"QUINCE", "15"}, {"DIECISEIS", "16"},
    {"DIECISIETE", "17"}, {"DIECIOCHO", "18"}, {"DIECINUEVE", "19"},
    {"VEINTE", "20"}, {"VEINTIUNO", "21"}, {"VEINTIDOS", "22"},
    {"VEINTITRES", "23"}, {"VEINTICUATRO", "24"}, {"VEINTICINCO", "25"},
    {"VEINTISEIS", "26"}, {"VEINTISIETE", "27"}, {"VEINTIOCHO", "28"},
    {"VEINTINUEVE", "29"}, {"TREINTA", "30"}, {"TREINTA Y UNO", "31"}
}
' Diccionario para los meses
Dim meses As New Dictionary(Of String, String) From {
    {"ENERO", "01"}, {"FEBRERO", "02"}, {"MARZO", "03"}, {"ABRIL", "04"},
    {"MAYO", "05"}, {"JUNIO", "06"}, {"JULIO", "07"}, {"AGOSTO", "08"},
    {"SEPTIEMBRE", "09"}, {"OCTUBRE", "10"}, {"NOVIEMBRE", "11"}, {"DICIEMBRE", "12"}
}
' Remover "a " si está presente
fechaEntrada = fechaEntrada.Replace("a ", "").Trim()
' Separar los elementos de la fecha
Dim partes As String() = fechaEntrada.Split(New String() {" de "}, StringSplitOptions.None)
If partes.Length = 3 Then
    ' Convertir el día
    Dim diaTexto As String = partes(0).Trim()
    Dim mesTexto As String = partes(1).Trim()
    Dim anioTexto As String = partes(2).Trim()
    ' Convertir año en texto a número (solo para el caso de "dos mil veinticuatro")
    Dim anioNumerico As String = ""
    If anioTexto = "DOS MIL VEINTICUATRO" Or anioTexto = "DOSMIL VEINTICUATRO" Then
        anioNumerico = "2024"
    ElseIf anioTexto = "DOS MIL VEINTITRES" Or anioTexto = "DOSMIL VEINTITRES" Then
        anioNumerico = "2023"
	 ElseIf anioTexto = "DOS MIL VEINTICINCO" Or anioTexto = "DOSMIL VEINTICINCO" Then
		anioNumerico = "2025"
  	ElseIf anioTexto = "DOS MIL VEINTISEIS" Or anioTexto = "DOSMIL VEINTISEIS" Then
		anioNumerico = "2026"
	ElseIf anioTexto = "DOS MIL VEINTISIETE" Or anioTexto = "DOSMIL VEINTISIETE" Then
		anioNumerico = "2027"
  	ElseIf anioTexto = "DOS MIL VEINTIOCHO" Or anioTexto = "DOSMIL VEINTIOCHO" Then
		anioNumerico = "2028"
    End If
    ' Validar si existen en los diccionarios
    If numeros.ContainsKey(diaTexto) And meses.ContainsKey(mesTexto) And anioNumerico <> "" Then
        fechaConvertida = numeros(diaTexto) & "/" & meses(mesTexto) & "/" & anioNumerico
    Else
        fechaConvertida = "Formato inválido"
    End If
Else
    fechaConvertida = "Formato inválido"
End If