import React from "react";
import { useNavigate } from "react-router-dom";
import { Setting } from "../../casualcms/domain/model";
import { AppContext } from "../../config";
import { DeletePopoverForm } from "../layout/confirm";
import { useAuth } from "../login/hooks";

type SettingDeletePopoverFormProps = {
  curSetting: Setting;
};

export const SettingDeletePopoverForm: React.FunctionComponent<
  SettingDeletePopoverFormProps
> = (props: SettingDeletePopoverFormProps) => {
  const config = React.useContext(AppContext);
  let auth = useAuth();
  let navigate = useNavigate();
  const token = auth.authenticatedUser?.token || "";
  const { curSetting } = props;
  const [confirmed, setConfirmed] = React.useState<boolean>(false);

  const onSubmit = async () => {
    await config.api.setting.deleteSetting(token, curSetting);
    setConfirmed(true);
  };

  React.useEffect(() => {
    if (confirmed) {
      navigate(`/admin/settings/${curSetting.meta.hostname}`);
    }
  }, [confirmed]);

  return (
    <DeletePopoverForm button_label="Delete this setting" onSubmit={onSubmit} />
  );
};
