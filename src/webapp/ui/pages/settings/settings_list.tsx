import React from "react";
import {
  Box,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";
import { Link, useParams } from "react-router-dom";
import {
  PartialSetting,
  PartialSettingType,
} from "../../../casualcms/domain/model";
import { ApiError } from "../../../casualcms/domain/ports";
import { AppConfig, useConfig } from "../../../config";
import { Loader } from "../../components/loader";
import { useAuth } from "../login/hooks";
import { SettingBreadcrumb } from "../../components/breadcrumb";

type SettingRowProps = {
  settingUrl: string | undefined;
  settingType: PartialSettingType;
};

type SettingsTableProps = {
  config: AppConfig;
  token: string;
  hostname: string;
  settingTypes: PartialSettingType[];
};

export const SettingRow: React.FunctionComponent<SettingRowProps> = (
  props: SettingRowProps
) => {
  const { settingUrl, settingType } = props;
  return (
    <Tr>
      <Td>
        <Link to={settingUrl || "#broken"}>{settingType.title}</Link>
      </Td>
    </Tr>
  );
};

export const SettingsTable: React.FunctionComponent<SettingsTableProps> = (
  props: SettingsTableProps
) => {
  const { config, token, hostname, settingTypes } = props;
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [settingsUrl, setSettingsUrl] = React.useState<{
    [key: string]: string;
  }>({});
  const [error, setError] = React.useState<ApiError>(null);

  React.useEffect(() => {
    async function loadSettings() {
      const settings = await config.api.setting.listSettings(token, hostname);
      settings
        .map((typ: PartialSetting[]) => {
          const settingsObj: { [key: string]: string } = {};
          settingTypes.map(
            (val) =>
              (settingsObj[
                val.key
              ] = `/admin/settings/${hostname}/${val.key}/new`)
          );
          typ.map((val) => {
            settingsObj[
              val.metadata.key
            ] = `/admin/settings/${hostname}/${val.metadata.key}/edit`;
          });
          setSettingsUrl(settingsObj);
        })
        .mapErr((err: ApiError) => setError(err));
      setIsLoading(false);
    }
    loadSettings();
    return () => {
      setIsLoading(true);
      setError(null);
      setSettingsUrl({});
    };
  }, []);

  if (isLoading) {
    return <Loader label="loading setting..." />;
  }
  return (
    <TableContainer>
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Setting Type</Th>
          </Tr>
        </Thead>
        <Tbody>
          {settingTypes.map((typ) => (
            <SettingRow
              settingType={typ}
              settingUrl={settingsUrl[typ.key]}
              key={typ.key}
            />
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  );
};

export const SettingList: React.FunctionComponent<{}> = () => {
  const config = useConfig();
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  let { hostname, settingType } = useParams<string>();
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [settingTypes, setSettingTypes] = React.useState<PartialSettingType[]>(
    []
  );
  const [error, setError] = React.useState<ApiError>(null);

  React.useEffect(() => {
    async function loadTypes() {
      const types = await config.api.settingType.listSettingTypes(token);
      types
        .map((typ: PartialSettingType[]) => setSettingTypes(typ))
        .mapErr((err: ApiError) => setError(err));
      setIsLoading(false);
    }
    if (token) {
      loadTypes();
    }
    return () => {
      setIsLoading(true);
      setError(null);
      setSettingTypes([]);
    };
  }, [auth, settingType]);

  if (isLoading) {
    return <Loader label="loading setting types..." />;
  }

  return (
    <Box minW="1440px">
      <SettingBreadcrumb hostname={hostname} />
      <Box maxW="1440px">
        <SettingsTable
          config={config}
          token={token}
          hostname={hostname || ""}
          settingTypes={settingTypes}
        />
      </Box>
    </Box>
  );
};
