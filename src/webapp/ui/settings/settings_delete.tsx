import React from "react";
import { Navigate } from "react-router-dom";
import { Setting } from "../../casualcms/domain/model";
import { AppContext } from "../../config";
import { DeletePopoverForm } from "../layout/confirm";
import { useAuth } from "../login/hooks";

type SettingDeletePopoverFormProps = {
  hostname: string;
  curSetting: Setting;
};

export const SettingDeletePopoverForm: React.FunctionComponent<
  SettingDeletePopoverFormProps
> = (props: SettingDeletePopoverFormProps) => {
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const { hostname, curSetting } = props;
  const [confirmed, setConfirmed] = React.useState<boolean>(false);

  const onSubmit = async () => {
    await config.api.setting.deleteSetting(token, hostname, curSetting);
    setConfirmed(true);
  };

  if (confirmed) {
    return <Navigate to={`/admin/settings/${hostname}`} replace />;
  }

  return (
    <DeletePopoverForm button_label="Delete this setting" onSubmit={onSubmit} />
  );
};
