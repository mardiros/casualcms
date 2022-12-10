import React from "react";
import { useNavigate } from "react-router-dom";
import { Site } from "../../../casualcms/domain/model";
import { useConfig } from "../../../config";
import { DeletePopoverForm } from "../../components/confirm";
import { useAuth } from "../login/hooks";

type SiteDeletePopoverFormProps = {
  curSite: Site;
};

export const SiteDeletePopoverForm: React.FunctionComponent<
  SiteDeletePopoverFormProps
> = (props: SiteDeletePopoverFormProps) => {
  const navigate = useNavigate();
  const config = useConfig();
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const curSite = props.curSite;

  const [confirmed, setConfirmed] = React.useState<boolean>(false);

  const onSubmit = async () => {
    await config.api.site.deleteSite(token, curSite.hostname);
    setConfirmed(true);
  };

  React.useEffect(() => {
    if (confirmed) {
      navigate("/admin/sites");
    }
  }, [confirmed]);

  return (
    <DeletePopoverForm button_label="Delete this site" onSubmit={onSubmit} />
  );
};
