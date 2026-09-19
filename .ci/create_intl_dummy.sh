#!/bin/bash
set -e
GTKADA_SRC="$1"
if [ ! -f "${GTKADA_SRC}/gtkada-intl.adb" ]; then
  cat > "${GTKADA_SRC}/gtkada-intl.adb" <<'EOF'
with Glib;
package body Gtkada.Intl is
   Default_Domain : String := "gtkada";
   procedure Setlocale (Category : Integer := LC_ALL; Locale : String := "") is
      pragma Unreferenced (Category, Locale);
   begin
      null;
   end Setlocale;
   function Gettext (Msg : Glib.UTF8_String) return Glib.UTF8_String is
   begin
      return Msg;
   end Gettext;
   function Dgettext (Domain : String; Msg : Glib.UTF8_String) return Glib.UTF8_String is
      pragma Unreferenced (Domain);
   begin
      return Msg;
   end Dgettext;
   function "-" (Msg : Glib.UTF8_String) return Glib.UTF8_String is
   begin
      return Msg;
   end "-";
   function Dcgettext (Domain : String; Msg : Glib.UTF8_String; Category : Integer) return Glib.UTF8_String is
      pragma Unreferenced (Domain, Category);
   begin
      return Msg;
   end Dcgettext;
   function Default_Text_Domain return String is
   begin
      return Default_Domain;
   end Default_Text_Domain;
   procedure Text_Domain (Domain : String := "") is
   begin
      if Domain /= "" then
         Default_Domain := Domain;
      end if;
   end Text_Domain;
   procedure Bind_Text_Domain (Domain : String; Dirname : String) is
      pragma Unreferenced (Domain, Dirname);
   begin
      null;
   end Bind_Text_Domain;
   procedure Bind_Text_Domain_Codeset (Domain : String; Codeset : String) is
      pragma Unreferenced (Domain, Codeset);
   begin
      null;
   end Bind_Text_Domain_Codeset;
   function Getlocale return String is
   begin
      return "C";
   end Getlocale;
end Gtkada.Intl;
EOF
  echo "Created dummy gtkada-intl.adb body"
fi
